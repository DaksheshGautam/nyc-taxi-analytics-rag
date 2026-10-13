"""Whitelist public project evidence, generate factual documents, index locally."""
from pathlib import Path
import csv,json,re,shutil,hashlib,html
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent

def build(source=None):
    source=Path(source or (ROOT.parent if (ROOT.parent/'data').is_dir() else ROOT/'corpus'))
    corpus=ROOT/'corpus';corpus.mkdir(exist_ok=True)
    chunks=[];manifest=[]
    def rows(name):return list(csv.DictReader((source/'data'/f'{name}.csv').open(encoding='utf-8-sig')))
    def n(v):return float(v)
    def fmt(v,d=0):return f'{n(v):,.{d}f}'
    def register(relative,title,kind):
        p=corpus/relative
        manifest.append({'path':relative,'title':title,'kind':kind,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    def add(identifier,title,text,relative,kind,**extra):
        chunks.append({'id':identifier,'title':title,'text':text.strip(),'source':relative,'kind':kind,**extra})
    def copy(relative):
        target=corpus/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if (source/relative).resolve()!=target.resolve():shutil.copy2(source/relative,target)
    # The report PDF itself is indexed with page locators, not just a text substitute.
    copy('Analysis_Report.pdf');register('Analysis_Report.pdf','Evidence-led analysis report','pdf')
    reader=PdfReader(corpus/'Analysis_Report.pdf')
    for page_no,page in enumerate(reader.pages,1):
        text=page.extract_text(extraction_mode='layout')
        text=re.sub(r'NYC YELLOW TAXI \| Source snapshot[^\n]*','',text)
        text=' '.join(text.split());words=text.split()
        title=f'Analysis report - page {page_no}'
        for start in range(0,len(words),120):
            part=' '.join(words[start:start+155])
            if part:add(f'report-p{page_no}-{start//120}',title,part,'Analysis_Report.pdf','report',page=page_no)
    documents=['DATA_DICTIONARY.md','QUALITY_INVESTIGATION.md','SCOPE.md','POSTGRESQL_MIGRATION.md','DETAILED_DATA_GUIDE.md']
    for name in documents:
        copy(name);register(name,name.replace('_',' ').replace('.md',''),'document')
        text=(corpus/name).read_text(encoding='utf-8-sig')
        for i,part in enumerate(re.split(r'\n(?=#{1,3} )',text)):
            lines=part.strip().splitlines();title=lines[0].lstrip('# ') if lines else name
            words=part.split()
            for start in range(0,len(words),120):
                piece=' '.join(words[start:start+160])
                if piece:add(f'doc-{name}-{i}-{start//120}',title,piece,name,'document')
    tables=['annual_2025','hourly_dashboard_2025','historical_comparable','historical_year','cleaning_funnel','cleaning_waterfall','zone_pickup_dropoff_2025','zone_balance_top20','airport_only_2025','payment_diagnostics','negative_money_patterns','negative_counterpart_check','jfk_within_zone_diagnostics','flex_negative_fare_values','weekday_heatmap_2025','daytype_hour_2025','fare_band_2025','sensitivity_2025','monthly_2025','borough_2025']
    for name in tables:
        relative='data/'+name+'.csv';copy(relative);register(relative,name.replace('_',' '),'table')
        for i,row in enumerate(rows(name),2):
            label=next((row[k] for k in ['zone','airport_group','payment_label','source_month','stage','year','distance_band','day_type'] if k in row),name)
            if name=='hourly_dashboard_2025':label='Pickup hour '+f'{int(row["hour"]):02}:00'
            if name=='weekday_heatmap_2025':label=row['weekday']+' pickup hour '+f'{int(row["hour"]):02}:00'
            text='Dataset: '+name+'. Population and units follow DATA_DICTIONARY.md. '+ '; '.join(k.replace('_',' ')+': '+str(v or 'NULL') for k,v in row.items())
            add(f'row-{name}-{i}',name.replace('_',' ')+' | '+label,text,relative,'table',row=i)
        # SQL is retained for audit, not treated as a computed answer by the retriever.
        sql_name=name if (source/'sql'/f'{name}.sql').exists() else 'airport_2025' if name=='airport_only_2025' else None
        if sql_name:
            sqlrel='sql/'+sql_name+'.sql'
            copy(sqlrel);register(sqlrel,sql_name+' calculation','sql')
    a=rows('annual_2025')[0];k=rows('hourly_kpis_2025')[0];h=rows('hourly_dashboard_2025');hc=rows('historical_comparable')
    pk=max(h,key=lambda r:n(r['trips']));fp=max(h,key=lambda r:n(r['fare_sum_usd']))
    pay=rows('payment_diagnostics');flex=next(r for r in pay if r['payment_type']=='0')
    neg=rows('negative_money_patterns');pair=rows('negative_counterpart_check')[0];jfk=rows('jfk_within_zone_diagnostics')[0]
    bal=rows('zone_pickup_dropoff_2025');nyc=[r for r in bal if r['borough'] in ['Manhattan','Queens','Brooklyn','Bronx','Staten Island']]
    positive=max(nyc,key=lambda r:n(r['net_dropoffs']));negative=min(nyc,key=lambda r:n(r['net_dropoffs']))
    facts=[]
    def fact(slug,question,answer,proof):facts.append(dict(id='fact-'+slug,title=question,text=answer,proof=proof))
    fact('peak-hour','What is the busiest pickup hour? Peak hourly trips and demand',f'For 2025 operational trips, the busiest pickup hour is {int(pk["hour"]):02}:00-{int(pk["hour"]):02}:59. It contains {fmt(pk["trips"])} annual pickups, {fmt(pk["avg_daily_trips"])} average daily pickups and {fmt(n(pk["trip_share"])*100,2)}% of operational trips. These are completed-record counts, not unmet demand.',['data/hourly_dashboard_2025.csv'])
    fact('fare-peak','When do recorded meter fare totals peak?',f'Recorded meter-fare totals peak at {int(fp["hour"]):02}:00 in 2025. Operational pickup counts peak at {int(pk["hour"]):02}:00. The fare series uses fare-eligible records; the pickup series uses all operational records. No causal explanation for the difference is established.',['data/hourly_dashboard_2025.csv'])
    fact('annual-trips','How many total operational trips and average daily trips are there?',f'The 2025 operational population is {fmt(a["trips"])} trips. Average daily operational activity is {fmt(n(a["trips"])/365)} trips, using all 365 calendar dates. The total is not the raw published count.',['data/annual_2025.csv'])
    fact('funnel','Why were 564,918 records excluded? What is the cleaning funnel?','Published 2025 records: 48,722,602. Operational trips: 48,157,684. Fare-eligible records: 44,727,165. Operational exclusions total 564,918: 214 pickups outside source month, 546,304 nonpositive durations and 18,400 durations over 180 minutes, in disjoint priority order. Missing timestamps add zero exclusions.',['data/cleaning_funnel.csv','data/cleaning_waterfall.csv'])
    fact('fare-eligibility','Why are 48.16 million operational trips different from 44.73 million fare eligible records?','The 48,157,684 operational trips include records that fail fare eligibility. A further 3,430,519 records are excluded from fare analysis: 2,853,180 negative fare/charge records, then 577,339 disputed payments with nonnegative money. The remaining 44,727,165 are fare eligible. Payment and money must be nonmissing; money nonnegative; payment not 4 or 6.',['data/cleaning_waterfall.csv'])
    fact('flex-fare','What does payment code 0 mean? Is it unspecified or unknown?',f'The TLC yellow taxi dictionary dated 18 March 2025 defines payment code 0 as Flex Fare. It is not missing or unspecified payment. Flex Fare has {fmt(flex["operational_trips"])} operational trips ({fmt(n(flex["operational_trips"])/n(a["trips"])*100,2)}%) and {fmt(flex["fare_n"])} eligible fare records. Code 5 Unknown contains only 2 operational records.',['data/payment_diagnostics.csv','QUALITY_INVESTIGATION.md'])
    fact('negative-money','Are negative fares refunds? What did the money investigation find?',f'Negative money is not established to represent refunds. Flex Fare contains {fmt(flex["negative_money_raw"])} raw negative-money records. Of these, {fmt(sum(n(r["fare_only_negative"]) for r in neg if r["payment_type"]=="0"))} have negative fare and nonnegative charge. The most frequent such fare value is -4.75 (1,048,380 raw records). The source dictionary does not explain the cause.',['data/payment_diagnostics.csv','data/negative_money_patterns.csv','data/flex_negative_fare_values.csv'])
    fact('counterpart','Does a matching positive counterpart prove refunds or duplicates?',f'Of {fmt(pair["negative_both_money_operational"])} operational records with both money values negative, {fmt(pair["exact_positive_counterpart_records"])} have at least one matching positive counterpart: timestamps, zone IDs and distance match and fare/charge have opposite signs and equal magnitudes. This is an existence test, not a one-to-one transaction match. It proves neither refunds nor duplication. No deduplication was applied.',['data/negative_counterpart_check.csv','QUALITY_INVESTIGATION.md'])
    fact('jfk-same-zone','Why are there JFK to JFK trips? What are the same-zone caveats?',f'PU132/DO132 means both endpoints share the JFK taxi zone, not identical GPS positions. There are {fmt(jfk["trips"])} operational records; {fmt(jfk["zero_distance_trips"])} ({fmt(n(jfk["zero_distance_trips"])/n(jfk["trips"])*100,2)}%) have zero recorded distance. Median duration is {fmt(jfk["median_duration_min"],1)} minutes; p90 {fmt(jfk["p90_duration_min"],1)} minutes. The cause and transaction validity are not established.',['data/jfk_within_zone_diagnostics.csv'])
    fact('arrivals','Which NYC zone has more drop-offs than pickups? Largest net arrivals',f'{positive["zone"]} has the largest positive annual NYC balance: {fmt(positive["dropoffs"])} drop-offs minus {fmt(positive["pickups"])} pickups = +{fmt(positive["net_dropoffs"])}. This is an observed endpoint difference, not a recommendation about taxi supply.',['data/zone_pickup_dropoff_2025.csv'])
    fact('departures','Which NYC zone has more pickups than drop-offs? Largest net departures',f'{negative["zone"]} has the largest negative annual NYC balance: {fmt(negative["dropoffs"])} drop-offs minus {fmt(negative["pickups"])} pickups = {fmt(negative["net_dropoffs"])}. Balance is drop-offs minus pickups; negative means more pickups.',['data/zone_pickup_dropoff_2025.csv'])
    fact('net-definition','How is pickup versus drop-off zone balance calculated?','Zone balance = drop-offs minus pickups. Each of the same 48,157,684 operational records contributes one pickup and one drop-off. Positive means more arrivals; negative means more departures. Global endpoint totals reconcile; NYC subtotals need not because other endpoints can be off-city or unknown.',['data/zone_pickup_dropoff_2025.csv'])
    fact('history-comparison','How did January August 2026 change versus 2025? Historical volume decrease',f'January-August 2026 has {fmt(hc[-1]["jan_aug_records"])} published records versus {fmt(hc[-2]["jan_aug_records"])} in January-August 2025, a {fmt(hc[-1]["yoy_pct"],1)}% change. These are raw source-file counts, not cleaned operational trips. Neither period is annualized; no cause is established.',['data/historical_comparable.csv'])
    fact('history-scope','Do you have every trip from previous years? What is the dataset coverage?','Historical coverage is January 2009 through August 2026: 212 verified monthly source-file footers. Earlier trip records were not downloaded or cleaned. Detailed operational analysis uses all twelve 2025 trip files. The 2026 period is partial, January-August only.',['SCOPE.md','Analysis_Report.pdf'])
    fact('median-duration','What are median trip duration and p90? Exact pooled statistics',f'The 2025 operational median duration is {fmt(a["median_duration_min"],1)} minutes and p90 is {fmt(a["p90_duration_min"],1)} minutes. Exact pooled SQL quantile_cont values are used. P90 is a percentile of recorded observations, not a guaranteed travel time. Monthly medians are not averaged into the annual median.',['data/annual_2025.csv','DATA_DICTIONARY.md'])
    fact('fare-median','What are median recorded meter fare and total charge?',f'For {fmt(a["fare_n"])} eligible 2025 records, median meter fare is USD {fmt(a["median_fare_usd"],2)} and median recorded total charge is USD {fmt(a["median_charge_usd"],2)}. Subtracting these medians does not produce the median surcharge. Monetary values are nominal USD.',['data/annual_2025.csv'])
    fact('fare-mean','What is average mean fare per trip and total charge?',f'For {fmt(a["fare_n"])} eligible 2025 records, mean recorded meter fare is USD {fmt(n(a["fare_sum_usd"])/n(a["fare_n"]),2)} and mean recorded total charge is USD {fmt(n(a["charge_sum_usd"])/n(a["fare_n"]),2)}. Each mean divides the selected monetary sum by its eligible record count.',['data/annual_2025.csv'])
    fact('fare-revenue','Is the 901.3 million fare total collected revenue, profit or earnings?',f'The 2025 eligible recorded meter-fare sum is USD {fmt(n(a["fare_sum_usd"])/1e6,1)} million. It is a sum of recorded fare_amount values, not a measurement of collected revenue, driver earnings or profit. Cash tips are absent; costs and driver shifts are not supplied.',['data/annual_2025.csv','Analysis_Report.pdf'])
    fact('distance','How are missing negative abnormal or zero distance records handled?','Distance summaries use nonmissing reported meter miles from 0 to 100 inclusive. Zero distance is retained. Negative, missing and above-100-mile distance values affect distance metrics only, not otherwise eligible operational counts. The annual distance median is 1.85 miles before display rounding. Unknown zones remain in global activity.',['DATA_DICTIONARY.md','data/annual_2025.csv'])
    fact('daily-denominator','How are trips by hour daily averages and weekday heatmap calculated?','Annual trips in each pickup hour are divided by all 365 calendar days. Weekday hourly patterns divide by 261 weekdays; weekend patterns by 104 weekend dates. Weekday-hour heatmap cells divide by the number of that weekday: Wednesday 53, other weekdays 52 in 2025. Missing date-zone activity is represented by zero rows in the Explorer calendar.',['DATA_DICTIONARY.md','Analysis_Report.pdf'])
    for r in rows('airport_only_2025'):
        fact('airport-'+r['airport_group'].lower().replace(' ','-'),r['airport_group']+' median and p90 travel duration sample size',f'For {r["airport_group"]} in 2025: {fmt(r["trips"])} operational trips, median duration {fmt(r["median_duration_min"],1)} minutes and p90 {fmt(r["p90_duration_min"],1)} minutes. Fare-eligible sample: {fmt(r["fare_n"])}. These are pooled recorded distributions, not forecasts or guaranteed time buffers.',['data/airport_only_2025.csv'])
    fact('filters','Can I average monthly medians or filter daily average and fares?','Explorer date, pickup borough and taxi zone filters apply to seven views. Daily average = selected trips / distinct selected calendar dates, including zero-activity rows. Mean fare = selected eligible fare sum / selected fare-eligible count. Stored group medians cannot be averaged into filtered medians. The other dashboards are fixed full-year reference views.',['DATA_DICTIONARY.md','Analysis_Report.pdf'])
    fact('limitations','Can the data explain causes, predict future demand, driver profit or taxi rebalancing?','No causal explanation, forecast, driver profit, utilization, unmet-demand estimate or optimal taxi allocation is established by this analysis. Completed trip records lack failed requests, passenger queues, vehicle availability, costs and driver-shift information. Negative-money meanings and short within-JFK records remain unresolved.',['Analysis_Report.pdf','QUALITY_INVESTIGATION.md'])
    faq=['# Verified evidence FAQ','Generated from the retained October 2026 snapshot. Detailed trip findings cover 2025. Each entry identifies supporting originals.']
    for item in facts:
        faq.extend(['','## '+item['title'],item['text'],'Evidence: '+ '; '.join(item['proof'])])
        add(item['id'],item['title'],item['text']+'\nEvidence: '+ '; '.join(item['proof']),'Verified_Evidence_FAQ.md','fact',evidence=item['proof'])
    (corpus/'Verified_Evidence_FAQ.md').write_text('\n'.join(faq),encoding='utf8');register('Verified_Evidence_FAQ.md','Verified evidence FAQ','generated')
    guide='''# Metric and population guide

## Three populations
Historical counts mean published source-file rows, before cleaning. Detailed 2025 operational trips require source-month-matched pickup, both timestamps and duration greater than zero and at most 180 minutes. Fare eligibility is an operational subset with nonmissing nonnegative fare/charge and payment not disputed or voided. Do not mix their denominators.

## Monetary fields
fare_amount is recorded meter fare; total_amount is the recorded total passenger charge. Cash tips are absent. Recorded sums do not establish collected revenue, profit or driver earnings. Means divide monetary sums by fare-eligible counts. Separate medians cannot be subtracted to obtain median surcharges.

## Percentiles and distance
SQL exact pooled quantile_cont calculates median and p90. Percentiles are not additive and stored group medians cannot be averaged. Distance metrics separately require reported distance from 0 through 100 miles inclusive. Zero distance remains eligible for distance and activity.

## Endpoint and map geography
Net zone balance equals drop-offs minus pickups. Positive means more recorded arrivals and negative more recorded departures. Both endpoint counts use the same operational records. Cross-boundary and unknown endpoints can prevent NYC subtotals balancing. Tableau's density map weights 259 representative NYC zone points by pickups; these are approximate zone locations, not trip GPS.

## Daily denominators
Hourly daily activity uses all 365 calendar days in 2025, or 261 weekdays and 104 weekend days. Heatmap weekday counts use actual occurrences. Selected Explorer daily averages use all selected dates, including zero-activity date-zone combinations. Fare means use selected eligible counts.

Evidence: DATA_DICTIONARY.md, Analysis_Report.pdf pages 2-4, 6-8 and 10; retained SQL summary tables.
'''
    limits='''# Questions the evidence cannot answer

## Causes and predictions
The analysis is descriptive. It does not identify causes of the 2026 matching-period volume difference, explain every negative-money record, establish why pickup and fare-total peaks differ, or forecast future activity. No claims about weather, policy or market causes are established.

## Financial and operational outcomes
There is no operating-cost, driver-shift, taxi-availability, failed-request or passenger-queue evidence. Driver earnings, profit, utilization, unmet demand, business savings and optimal fleet allocation are not measured. Reported fares are recorded fields, not collected revenue. Cash tips are absent.

## Transactions and short trips
An opposite-money counterpart existence check is not a one-to-one refund or duplicate match. Same airport zone IDs do not establish identical GPS locations. Short and zero-distance within-JFK records require transaction or vendor context before their causes can be explained.

## Coverage and source updates
The source snapshot was checked 12 October 2026. Detailed trip analysis covers January-December 2025; historical raw footer counts cover January 2009-August 2026. Earlier trip-level fields and future or live data are outside this knowledge base. Raw flag counts overlap; do not sum them as exclusions.

Evidence: Analysis_Report.pdf pages 3-4 and 8-10; QUALITY_INVESTIGATION.md; SCOPE.md. This document states evidence boundaries, not new empirical findings.
'''
    for name,title,text in [('Metric_Guide.md','Metric and population guide',guide),('Evidence_Limits.md','Evidence boundaries',limits)]:
        (corpus/name).write_text(text,encoding='utf8');register(name,title,'generated')
        for i,part in enumerate(re.split(r'\n(?=## )',text)):
            add('guide-'+name+'-'+str(i),part.splitlines()[0].lstrip('# '),part,name,'guide')
    manifest.sort(key=lambda m:m['path'])
    output={'version':1,'snapshot':'2026-10-12','retrieval':'BM25 lexical retrieval with small domain synonym expansion','manifest':manifest,'chunks':chunks}
    (ROOT/'knowledge.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    checks={'unique_chunk_ids':len({c['id'] for c in chunks})==len(chunks),'report_pages_indexed':{c.get('page') for c in chunks if c['kind']=='report'}==set(range(1,len(reader.pages)+1)),'all_source_paths_exist':all((corpus/c['source']).is_file() for c in chunks),'funnel_reconciles':[int(r['records']) for r in rows('cleaning_funnel')]==[48722602,48157684,44727165],'endpoint_totals_reconcile':sum(int(r['pickups']) for r in bal)==sum(int(r['dropoffs']) for r in bal)==48157684}
    assert all(checks.values()),checks
    result={'sources':len(manifest),'chunks':len(chunks),'pdf_pages':len(reader.pages),'generated_faq_entries':len(facts),'checks':checks,'live_llm_tested':False}
    (ROOT/'index_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
if __name__=='__main__':build()
