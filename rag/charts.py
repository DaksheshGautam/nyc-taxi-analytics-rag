"""Question-relevant charts from fixed, verified analytical tables."""
import csv,re,hashlib,json
import pandas as pd
import altair as alt
from rag import ROOT
from cloud_store import connect

TABLES={'hour':'hourly_dashboard_2025','weekpart':'daytype_hour_2025','heatmap':'weekday_heatmap_2025','zones':'zone_pickup_dropoff_2025','months':'monthly_2025','cleaning':'cleaning_funnel','payment':'payment_diagnostics'}

def choose(question):
    q=question.lower()
    if any(y!='2025' for y in re.findall(r'\b20\d{2}\b',q)):return None
    if any(w in q for w in ['excluded','cleaning','eligible','funnel']):return 'cleaning'
    if 'payment' in q:return 'payment'
    if any(w in q for w in ['drop-off','dropoff','drop-offs','dropoffs','zone balance','zones have']):return 'zones'
    if 'weekend' in q:return 'weekpart'
    if 'heatmap' in q or ('weekday' in q and 'hour' in q):return 'heatmap'
    if any(w in q for w in ['hour','busiest','peak']):return 'hour'
    if any(w in q for w in ['month','season','annual','trips','trip trend','fare','revenue']):return 'months'
    return None

def records(db,kind,kb):
    name=TABLES[kind]
    if db.get('url'):
        with connect(db) as c:
            cur=c.execute('SELECT * FROM results.'+name+' LIMIT 500')
            return pd.DataFrame(cur.fetchall(),columns=[x.name for x in cur.description]),'Neon results.'+name
    path='data/'+name+'.csv';data=(ROOT/'corpus'/path).read_bytes()
    expected=next(m['sha256'] for m in kb.manifest if m['path']==path)
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Chart evidence checksum mismatch.')
    return pd.read_csv(ROOT/'corpus'/path),path

def filtered_records(db,selection,question):
    from detailed_store import GRAINS
    table,datecol,allowed=GRAINS[selection['scope']['grain']]
    dimension='pickup_hour' if 'hour' in question.lower() and 'pickup_hour' in allowed else datecol
    # SQL/parameters were produced by the validated, fixed summary builder.
    where=selection['sql'].split(' WHERE ',1)[1]
    query='SELECT '+dimension+' AS bucket,sum(trips)::bigint AS trips,sum(fare_n)::bigint AS fare_n,sum(fare_sum_usd) AS fare_sum_usd,sum(fare_sum_usd)/NULLIF(sum(fare_n),0) AS mean_fare_usd FROM detail.'+table+' WHERE '+where+' GROUP BY '+dimension+' ORDER BY '+dimension+' LIMIT 366'
    with connect(db) as c:
        cur=c.execute(query,selection['parameters']);df=pd.DataFrame(cur.fetchall(),columns=[x.name for x in cur.description])
    return df,dimension,'Neon detail.'+table,query

def theme(chart):
    return chart.properties(height=280).configure(background='#252D3A').configure_view(stroke=None).configure_axis(labelColor='#A0A8B5',titleColor='#F7F8FA',gridColor='#3A4352').configure_legend(labelColor='#A0A8B5',titleColor='#F7F8FA').configure_title(color='#F7F8FA',anchor='start',fontSize=16)

def render(st,question,db,kb,selection=None):
    kind=choose(question)
    if selection:
        df,dimension,source,query=filtered_records(db,selection,question)
        if df.empty:return
        st.subheader('Your selected data, visually')
        st.caption(selection['scope']['grain']+' · '+selection['scope']['start']+' through '+selection['scope']['end']+' · Filters: '+json.dumps(selection['scope']['filters']))
        x=alt.X('bucket:O',title='Pickup hour' if dimension=='pickup_hour' else 'Pickup date' if dimension=='pickup_date' else 'Source month')
        chart=alt.Chart(df).mark_bar(color='#3B82B8').encode(x=x,y=alt.Y('trips:Q',title='Operational trips'),tooltip=['bucket','trips','fare_n']).properties(title='Operational trip volume')
        st.altair_chart(theme(chart),use_container_width=True)
        if any(w in question.lower() for w in ['fare','revenue','money','charge']):
            metric='mean_fare_usd' if any(w in question.lower() for w in ['average','mean']) else 'fare_sum_usd'
            st.altair_chart(theme(alt.Chart(df).mark_line(color='#36A596',point=True).encode(x=x,y=alt.Y(metric+':Q',title='Mean meter fare (USD)' if metric=='mean_fare_usd' else 'Recorded meter fare total (USD)'),tooltip=['bucket',metric]).properties(title='Fare-eligible records')),use_container_width=True)
    elif kind:
        df,source=records(db,kind,kb);st.subheader('The numbers, visually');st.caption('2025 operational analysis · Fare amounts use fare-eligible records. Hover for exact values.')
        if kind=='hour':
            peak=int(df.loc[df['trips'].idxmax(),'hour'])
            chart=alt.Chart(df).mark_bar().encode(x=alt.X('hour:O',title='Pickup hour (0–23)'),y=alt.Y('avg_daily_trips:Q',title='Average daily trips'),color=alt.condition(alt.datum.hour==peak,alt.value('#F7C948'),alt.value('#3B82B8')),tooltip=['hour','trips','fare_n',alt.Tooltip('avg_daily_trips:Q',format=',.2f')]).properties(title='Trips by pickup hour · 365 calendar days')
            st.altair_chart(theme(chart),use_container_width=True)
            if any(w in question.lower() for w in ['fare','revenue','money','charge']):
                metric='mean_fare_usd' if any(w in question.lower() for w in ['average fare','mean fare']) else 'avg_daily_fare_usd'
                chart=alt.Chart(df).mark_line(color='#36A596',point=True).encode(x=alt.X('hour:O',title='Pickup hour'),y=alt.Y(metric+':Q',title='Mean meter fare (USD)' if metric=='mean_fare_usd' else 'Average daily meter fares (USD)'),tooltip=['hour','fare_n',alt.Tooltip(metric+':Q',format=',.2f')]).properties(title='Recorded meter fares by hour')
                st.altair_chart(theme(chart),use_container_width=True)
        elif kind=='weekpart':
            df['daily_trips']=pd.to_numeric(df['trips'])/pd.to_numeric(df['calendar_days'])
            chart=alt.Chart(df).mark_line(point=True).encode(x=alt.X('hour:O',title='Pickup hour'),y=alt.Y('daily_trips:Q',title='Average trips per calendar day'),color=alt.Color('day_type:N',scale=alt.Scale(range=['#3B82B8','#F7C948']),title='Day type'),tooltip=['day_type','hour','calendar_days',alt.Tooltip('daily_trips:Q',format=',.2f')]).properties(title='Weekday and weekend demand')
            st.altair_chart(theme(chart),use_container_width=True)
        elif kind=='heatmap':
            chart=alt.Chart(df).mark_rect().encode(x=alt.X('hour:O',title='Pickup hour'),y=alt.Y('weekday:N',sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],title='Weekday'),color=alt.Color('avg_daily_trips:Q',scale=alt.Scale(range=['#252D3A','#3B82B8','#F7C948']),title='Average daily trips'),tooltip=['weekday','hour','calendar_days',alt.Tooltip('avg_daily_trips:Q',format=',.2f')]).properties(title='Day and hour demand')
            st.altair_chart(theme(chart),use_container_width=True)
        elif kind=='zones':
            df=df[df['borough'].isin(['Manhattan','Queens','Brooklyn','Bronx','Staten Island'])].copy();df=df.loc[df['net_dropoffs'].abs().nlargest(12).index]
            chart=alt.Chart(df).mark_bar().encode(y=alt.Y('zone:N',sort='-x',title='NYC taxi zone'),x=alt.X('net_dropoffs:Q',title='Drop-offs minus pickups'),color=alt.condition(alt.datum.net_dropoffs>=0,alt.value('#36A596'),alt.value('#D97757')),tooltip=['zone','borough','pickups','dropoffs','net_dropoffs']).properties(title='12 NYC zones with the largest absolute imbalance')
            st.altair_chart(theme(chart).properties(height=360),use_container_width=True);st.caption('Positive: more drop-offs. Negative: more pickups. This does not establish unmet demand.')
        elif kind=='months':
            df=df.sort_values('source_month');metric='trips';title='Operational trips';color='#3B82B8'
            if any(w in question.lower() for w in ['fare','revenue']):
                metric='fare_sum_usd';title='Recorded meter fare total (USD)';color='#36A596'
                if any(w in question.lower() for w in ['average','mean']):
                    df['mean_fare_usd']=df['fare_sum_usd']/df['fare_n'].replace(0,float('nan'));metric='mean_fare_usd';title='Mean meter fare (USD)'
            chart=alt.Chart(df).mark_line(color=color,point=True).encode(x=alt.X('source_month:O',title='Source month'),y=alt.Y(metric+':Q',title=title),tooltip=['source_month',metric,'fare_n']).properties(title='Monthly '+title.lower())
            st.altair_chart(theme(chart),use_container_width=True)
        elif kind=='payment':
            chart=alt.Chart(df).mark_bar().encode(x=alt.X('payment_label:N',title='Recorded payment type'),y=alt.Y('operational_trips:Q',title='Operational trips'),color=alt.Color('payment_label:N',scale=alt.Scale(range=['#7778B4','#36A596','#F7C948','#8299B0','#A0A8B5','#D97757']),legend=None),tooltip=['payment_label','raw_records','operational_trips','fare_n']).properties(title='Trip volume by payment category')
            st.altair_chart(theme(chart),use_container_width=True);st.caption('Code 0 is Flex Fare. These recorded categories do not establish reasons for missing or negative amounts.')
        else:
            chart=alt.Chart(df).mark_bar(color='#F7C948').encode(y=alt.Y('stage:N',sort=alt.SortField(field='stage_no',order='ascending'),title=None),x=alt.X('records:Q',title='Records'),tooltip=['stage','records']).properties(title='From published records to analysis populations')
            st.altair_chart(theme(chart),use_container_width=True);st.caption('Stages are nested populations; do not add the bars together.')
    else:return
    st.caption('Chart source: '+source)
    with st.expander('Download chart data'):
        st.download_button('Download plotted numbers',df.to_csv(index=False),'nyc_taxi_chart_data.csv','text/csv')
