"""Parameterized queries over explicit, compatible aggregate dimensions."""
import datetime,json,hashlib
from cloud_store import connect

GRAINS={
 'Daily pickup zone and hour':('daily_hour_pickup_zone','pickup_date',('pickup_zone','pickup_hour')),
 'Daily hour and payment':('daily_hour_payment','pickup_date',('pickup_hour','payment_type')),
 'Daily drop-off zone':('daily_dropoff_zone','pickup_date',('dropoff_zone',)),
 'Monthly pickup–drop-off route':('monthly_route','source_month',('pickup_zone','dropoff_zone')),
 'Monthly pickup zone, hour and payment':('monthly_zone_hour_payment','source_month',('pickup_zone','pickup_hour','payment_type')),
}

def zones(db):
    with connect(db) as c:
        return c.execute("SELECT locationid,borough,zone FROM taxi_analysis.zones WHERE borough IN ('Manhattan','Brooklyn','Queens','Bronx','Staten Island') ORDER BY borough,zone").fetchall()

def summary(db,grain,start,end,filters):
    table,datecol,allowed=GRAINS[grain]
    if not isinstance(start,datetime.date) or not isinstance(end,datetime.date) or not datetime.date(2025,1,1)<=start<=end<=datetime.date(2025,12,31):raise ValueError('Choose a valid 2025 date range.')
    if set(filters)-set(allowed):raise ValueError('These dimensions are unavailable together.')
    params=[str(start)[:7] if datecol=='source_month' else start,str(end)[:7] if datecol=='source_month' else end]
    where=[datecol+' BETWEEN %s AND %s']
    for key,value in filters.items():
        if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=265:raise ValueError('Invalid filter.')
        if key=='pickup_hour' and value>23:raise ValueError('Invalid hour.')
        if key=='payment_type' and value>6:raise ValueError('Invalid payment type.')
        where.append(key+'=%s');params.append(value)
    query='''SELECT count(*) AS retained_groups,COALESCE(sum(trips),0)::bigint AS operational_trips,
COALESCE(sum(fare_n),0)::bigint AS fare_eligible_records,
sum(fare_sum_usd) AS recorded_meter_fare_usd,
sum(charge_sum_usd) AS recorded_total_charge_usd,
sum(fare_sum_usd)/NULLIF(sum(fare_n),0) AS mean_meter_fare_usd,
sum(duration_sum_min)/NULLIF(sum(trips),0) AS mean_duration_min,
sum(distance_sum_mi)/NULLIF(sum(distance_n),0) AS mean_valid_distance_mi,
sum(card_tip_sum_usd)/NULLIF(sum(card_tip_n),0) AS mean_recorded_card_tip_usd
FROM detail.'''+table+' WHERE '+' AND '.join(where)
    with connect(db) as c:
        cursor=c.execute(query,params);row=cursor.fetchone();data=dict(zip([x.name for x in cursor.description],row))
    scope={'grain':grain,'start':str(params[0]),'end':str(params[1]),'filters':filters,'date_basis':'pickup date / source month','period':'2025'}
    body=json.dumps({'scope':scope,'results':data},default=str,indent=2)
    chunk={'id':'live-'+hashlib.sha256(body.encode()).hexdigest()[:16],'kind':'database','title':'Selected Neon query results','source':'Neon detail.'+table,'text':body,'page':None,'row':None}
    return {'data':data,'scope':scope,'sql':query,'parameters':[str(p) for p in params],'chunk':chunk}
