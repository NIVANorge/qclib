# Quality Control tests 

Quality control tests are developed for several NIVA projects  
Current QC tests module is based on three documents: 

1. CMEMS Quality Control of Biogeochemical Measurements
http://archimer.ifremer.fr/doc/00251/36232/34792.pdf   
DOI http://doi.org/10.13155/36232

1. EuroGOOS DATA-MEQ working group (2010). 
Recommendations for in-situ data Near Real Time Quality Control. https://doi.org/10.13155/36230
https://archimer.ifremer.fr/doc/00251/36230/ 

1. Catherine Schmechtig, Virginie Thierry and the Bio Argo Team (2015). 
Argo Quality Control Manual For Biogeochemical Data. http://dx.doi.org/10.13155/40879
https://archimer.ifremer.fr/doc/00298/40879/42267.pdf


Flags meaning: 

* 1  is PASSED 
* -1 is FAILED 
* 0 is NOT TESTED

### real Time QC Tests  (class QCTests)

#### 1. Frozen test

The tests checks if 4 consecutive values before the tested value are equal. 

dataframe is reversed in time (df[0] is the latest element) 

array [5.,5., 5.,5., 5.,0.,1.] gives [-1,1, 1,0, 0,0,0] 

#### 2. Range test

`def range_test(clf, meta, data, **opts)`

The Function is used by Global range test , Local range test

Description:

        Checks that data is within a specified range.Accepts time range 
        and geographic range. The latter is based on minimum and maximum 
        latitudes and longitudes values. An later improvement could be
        to accept a geographic box.  
        
        Options:  
               
        * min    : minimum value (inclusive)
        * max    : maximum value (inclusive)
        * day_min: minimum date for which the test applies,
                   can be `py:class:datetime.date` or a decimal date
                   relative to 1950-01-01
        * day_max: maximum date for which the test applies (same format as `day_min`) 
        * lat_min: minimum latitude for which the test applies
        * lat_max: maximum latitude for which the test applies
        * lon_min: minimum longitude for which the test applies
        * lon_max: maximum longitude for which the test applies
        * area   : dictionary of polygon edges, with keys 'lat' and 'lon'. 
                   These should be listed in CW order       
        Meta:        
        * time: corresponding array of time (relative to 1950-01-01)
        * lat : corresponding array of latitudes
        * lon : corresponding array of longitudes   
        
   
Temperature thresholds for Baltic Sea are based on http://www.helcom.fi/baltic-sea-trends/environment-fact-sheets/hydrography/development-of-sea-surface-temperature-in-the-baltic-sea/      


![Areas for Local Range Test](../figs/Local_range_test_areas.png) 


#### 3.Spike test

Tests the difference between sequential measurements. 

Based on http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf 

Array to test [V1,V2,V3]

Only V2 is being tested for a spike: 
      
        K_difference = abs(V2-(V3+V1)/2) - abs((V3_V1)/2)

        if K_difference > Threshold :
            V2 flag = -1 

        V1,V3 cannot be tested here. 

What should the function return? 

Spike test should be done in a delayed mode. 
        

TODO: 
* Tests/flags Hierarchy description 
* More tests description 
* Visualize ranges ?

        
