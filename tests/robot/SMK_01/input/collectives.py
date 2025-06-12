collectives = {
   "identifier": "identifier",
   "npv_1_percent": "net_present_value.value[(net_present_value.interest_rate==1) & (net_present_value.time_point == 2055)]",
   "npv_2_percent": "net_present_value.value[(net_present_value.interest_rate==2) & (net_present_value.time_point == 2055)]",
   "npv_3_percent": "net_present_value.value[(net_present_value.interest_rate==3) & (net_present_value.time_point == 2055)]",
   "npv_4_percent": "net_present_value.value[(net_present_value.interest_rate==4) & (net_present_value.time_point == 2055)]",
   "npv_5_percent": "net_present_value.value[(net_present_value.interest_rate==5) & (net_present_value.time_point == 2075)]",
   "stock_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 2025)]",
   "stock_1": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 2035)]",
   "stock_2": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 2045)]",
   "stock_3": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 2055)]",
   "harvest_period_1": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & (cross_cutting.time_point >= 2025) & (cross_cutting.time_point < 2035)]",
   "harvest_period_2": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & (cross_cutting.time_point >= 2035) & (cross_cutting.time_point < 2045)]",
   "harvest_period_3": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & (cross_cutting.time_point >= 2045) & (cross_cutting.time_point < 2055)]"
}
