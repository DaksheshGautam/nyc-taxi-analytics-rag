"""Verify displayed chart populations, scope routing and chart validity."""
import unittest
from rag import KnowledgeBase
from charts import choose,records,render

class Display:
    def __init__(self):self.charts=[]
    def subheader(self,*a,**k):pass
    def caption(self,*a,**k):pass
    def altair_chart(self,chart,**k):self.charts.append(chart.to_dict())
    def expander(self,*a,**k):return self
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def download_button(self,*a,**k):pass

class ChartTests(unittest.TestCase):
    def test_routes(self):
        self.assertEqual(choose('Compare weekday and weekend hourly demand'),'weekpart')
        self.assertEqual(choose('Which zones have more drop-offs than pickups?'),'zones')
        self.assertIsNone(choose('Busiest hour in 2026?'))
        self.assertIsNone(choose('Average fare at 18:00 in January 2025?'))
        self.assertIsNone(choose('Why does demand change?'))
    def test_complete_populations(self):
        kb=KnowledgeBase()
        for kind in ['hour','weekpart','heatmap','months']:
            frame,_=records({},kind,kb)
            self.assertEqual(int(frame['trips'].sum()),48157684)
            self.assertEqual(int(frame['fare_n'].sum()),44727165)
        hour,_=records({},'hour',kb)
        self.assertEqual(len(hour),24)
        self.assertEqual(int(hour.loc[hour['trips'].idxmax(),'hour']),18)
        self.assertEqual(int(hour.loc[hour['fare_sum_usd'].idxmax(),'hour']),17)
    def test_chart_specs(self):
        kb=KnowledgeBase()
        for q in ['Busiest hour and fare revenue','Weekday versus weekend demand','Weekday hour heatmap','Zone balance','Monthly trip trend','Monthly average fare','Payment types','Excluded records cleaning']:
            ui=Display();render(ui,q,{},kb)
            self.assertTrue(ui.charts,q)
            self.assertEqual(ui.charts[0]['config']['background'],'#252D3A')
    def test_hour_fare_and_cleaning_comparison_has_all_charts(self):
        ui=Display();render(ui,'Compare peak hour and recorded fare totals and explain cleaning exclusions in 2025',{},KnowledgeBase())
        self.assertEqual(len(ui.charts),3)

if __name__=='__main__':unittest.main()
