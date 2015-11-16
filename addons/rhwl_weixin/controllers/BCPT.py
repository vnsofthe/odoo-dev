# -*- coding: utf-8 -*-
import math
class RiskCalculator():
    NumCovPattInGailModel = 216
    bet2 = [[0 for i in range(12)] for j in range(8)]
    bet = [0 for i in range(8)]
    
    rf = [0 for i in range(2)]
    abs = [0 for i in range(216)]
    rlan = [0 for i in range(14)]
    rmu = [0 for i in range(14)]
    sumb = [0 for i in range(216)]
    sumbb = [0 for i in range(216)]
    t = [0 for i in range(15)]
    rmu2 = [[0 for i in range(12)] for j in range(14)]
    rlan2 = [[0 for i in range(12)] for j in range(14)]
    rf2 = [[0 for i in range(13)] for j in range(2)] 
    
    
    def __init__(self):
        self.t[0] = 20.0
        self.t[1] = 25.0
        self.t[2] = 30.0
        self.t[3] = 35.0
        self.t[4] = 40.0
        self.t[5] = 45.0
        self.t[6] = 50.0
        self.t[7] = 55.0
        self.t[8] = 60.0
        self.t[9] = 65.0
        self.t[10] = 70.0
        self.t[11] = 75.0
        self.t[12] = 80.0
        self.t[13] = 85.0
        self.t[14] = 90.0
    
        self.rmu2[0][0] = 49.3 * 0.00001
        self.rmu2[1][0] = 53.1 * 0.00001
        self.rmu2[2][0] = 62.5 * 0.00001
        self.rmu2[3][0] = 82.5 * 0.00001
        self.rmu2[4][0] = 130.7 * 0.00001
        self.rmu2[5][0] = 218.1 * 0.00001
        self.rmu2[6][0] = 365.5 * 0.00001
        self.rmu2[7][0] = 585.2 * 0.00001
        self.rmu2[8][0] = 943.9 * 0.00001
        self.rmu2[9][0] = 1502.8 * 0.00001
        self.rmu2[10][0] = 2383.9 * 0.00001
        self.rmu2[11][0] = 3883.2 * 0.00001
        self.rmu2[12][0] = 6682.8 * 0.00001
        self.rmu2[13][0] = 14490.8 * 0.00001

        self.rmu2[0][1] = 0.00074354
        self.rmu2[1][1] = 0.00101698
        self.rmu2[2][1] = 0.00145937
        self.rmu2[3][1] = 0.00215933
        self.rmu2[4][1] = 0.00315077
        self.rmu2[5][1] = 0.00448779
        self.rmu2[6][1] = 0.00632281
        self.rmu2[7][1] = 0.00963037
        self.rmu2[8][1] = 0.01471818
        self.rmu2[9][1] = 0.02116304
        self.rmu2[10][1] = 0.03266035
        self.rmu2[11][1] = 0.04564087
        self.rmu2[12][1] = 0.06835185
        self.rmu2[13][1] = 0.13271262

        self.rmu2[0][2] = 43.7 * 0.00001
        self.rmu2[1][2] = 53.3 * 0.00001
        self.rmu2[2][2] = 70.0 * 0.00001
        self.rmu2[3][2] = 89.7 * 0.00001
        self.rmu2[4][2] = 116.3 * 0.00001
        self.rmu2[5][2] = 170.2 * 0.00001
        self.rmu2[6][2] = 264.6 * 0.00001
        self.rmu2[7][2] = 421.6 * 0.00001
        self.rmu2[8][2] = 696.0 * 0.00001
        self.rmu2[9][2] = 1086.7 * 0.00001
        self.rmu2[10][2] = 1685.8 * 0.00001
        self.rmu2[11][2] = 2515.6 * 0.00001
        self.rmu2[12][2] = 4186.6 * 0.00001
        self.rmu2[13][2] = 8947.6 * 0.00001

        self.rmu2[0][3] = 44.12 * 0.00001
        self.rmu2[1][3] = 52.54 * 0.00001
        self.rmu2[2][3] = 67.46 * 0.00001
        self.rmu2[3][3] = 90.92 * 0.00001
        self.rmu2[4][3] = 125.34 * 0.00001
        self.rmu2[5][3] = 195.70 * 0.00001
        self.rmu2[6][3] = 329.84 * 0.00001
        self.rmu2[7][3] = 546.22 * 0.00001
        self.rmu2[8][3] = 910.35 * 0.00001
        self.rmu2[9][3] = 1418.54 * 0.00001
        self.rmu2[10][3] = 2259.35 * 0.00001
        self.rmu2[11][3] = 3611.46 * 0.00001
        self.rmu2[12][3] = 6136.26 * 0.00001
        self.rmu2[13][3] = 14206.63 * 0.00001

        self.rmu2[0][4] = 0.00074354
        self.rmu2[1][4] = 0.00101698
        self.rmu2[2][4] = 0.00145937
        self.rmu2[3][4] = 0.00215933
        self.rmu2[4][4] = 0.00315077
        self.rmu2[5][4] = 0.00448779
        self.rmu2[6][4] = 0.00632281
        self.rmu2[7][4] = 0.00963037
        self.rmu2[8][4] = 0.01471818
        self.rmu2[9][4] = 0.02116304
        self.rmu2[10][4] = 0.03266035
        self.rmu2[11][4] = 0.04564087
        self.rmu2[12][4] = 0.06835185
        self.rmu2[13][4] = 0.13271262

        self.rmu2[0][5] = 43.7 * 0.00001
        self.rmu2[1][5] = 53.3 * 0.00001
        self.rmu2[2][5] = 70.0 * 0.00001
        self.rmu2[3][5] = 89.7 * 0.00001
        self.rmu2[4][5] = 116.3 * 0.00001
        self.rmu2[5][5] = 170.2 * 0.00001
        self.rmu2[6][5] = 264.6 * 0.00001
        self.rmu2[7][5] = 421.6 * 0.00001
        self.rmu2[8][5] = 696.0 * 0.00001
        self.rmu2[9][5] = 1086.7 * 0.00001
        self.rmu2[10][5] = 1685.8 * 0.00001
        self.rmu2[11][5] = 2515.6 * 0.00001
        self.rmu2[12][5] = 4186.6 * 0.00001
        self.rmu2[13][5] = 8947.6 * 0.00001

        self.rlan2[0][0] = 1.0 * 0.00001
        self.rlan2[1][0] = 7.6 * 0.00001
        self.rlan2[2][0] = 26.6 * 0.00001
        self.rlan2[3][0] = 66.1 * 0.00001
        self.rlan2[4][0] = 126.5 * 0.00001
        self.rlan2[5][0] = 186.6 * 0.00001
        self.rlan2[6][0] = 221.1 * 0.00001
        self.rlan2[7][0] = 272.1 * 0.00001
        self.rlan2[8][0] = 334.8 * 0.00001
        self.rlan2[9][0] = 392.3 * 0.00001
        self.rlan2[10][0] = 417.8 * 0.00001
        self.rlan2[11][0] = 443.9 * 0.00001
        self.rlan2[12][0] = 442.1 * 0.00001
        self.rlan2[13][0] = 410.9 * 0.00001

        self.rlan2[0][1] = 0.00002696
        self.rlan2[1][1] = 0.00011295
        self.rlan2[2][1] = 0.00031094
        self.rlan2[3][1] = 0.00067639
        self.rlan2[4][1] = 0.00119444
        self.rlan2[5][1] = 0.00187394
        self.rlan2[6][1] = 0.00241504
        self.rlan2[7][1] = 0.00291112
        self.rlan2[8][1] = 0.00310127
        self.rlan2[9][1] = 0.00366560
        self.rlan2[10][1] = 0.00393132
        self.rlan2[11][1] = 0.00408951
        self.rlan2[12][1] = 0.00396793
        self.rlan2[13][1] = 0.00363712
    
        self.rlan2[0][2] = 2.00 * 0.00001
        self.rlan2[1][2] = 7.10 * 0.00001
        self.rlan2[2][2] = 19.70 * 0.00001
        self.rlan2[3][2] = 43.80 * 0.00001
        self.rlan2[4][2] = 81.10 * 0.00001
        self.rlan2[5][2] = 130.70 * 0.00001
        self.rlan2[6][2] = 157.40 * 0.00001
        self.rlan2[7][2] = 185.70 * 0.00001
        self.rlan2[8][2] = 215.10 * 0.00001
        self.rlan2[9][2] = 251.20 * 0.00001
        self.rlan2[10][2] = 284.60 * 0.00001
        self.rlan2[11][2] = 275.70 * 0.00001
        self.rlan2[12][2] = 252.30 * 0.00001
        self.rlan2[13][2] = 203.90 * 0.00001
    
        self.rlan2[0][3] = 1.22 * 0.00001
        self.rlan2[1][3] = 7.41 * 0.00001
        self.rlan2[2][3] = 22.97 * 0.00001
        self.rlan2[3][3] = 56.49 * 0.00001
        self.rlan2[4][3] = 116.45 * 0.00001
        self.rlan2[5][3] = 195.25 * 0.00001
        self.rlan2[6][3] = 261.54 * 0.00001
        self.rlan2[7][3] = 302.79 * 0.00001
        self.rlan2[8][3] = 367.57 * 0.00001
        self.rlan2[9][3] = 420.29 * 0.00001
        self.rlan2[10][3] = 473.08 * 0.00001
        self.rlan2[11][3] = 494.25 * 0.00001
        self.rlan2[12][3] = 479.76 * 0.00001
        self.rlan2[13][3] = 401.06 * 0.00001
    
        self.rlan2[0][4] = 0.00002696
        self.rlan2[1][4] = 0.00011295
        self.rlan2[2][4] = 0.00031094
        self.rlan2[3][4] = 0.00067639
        self.rlan2[4][4] = 0.00119444
        self.rlan2[5][4] = 0.00187394
        self.rlan2[6][4] = 0.00241504
        self.rlan2[7][4] = 0.00291112
        self.rlan2[8][4] = 0.00310127
        self.rlan2[9][4] = 0.00366560
        self.rlan2[10][4] = 0.00393132
        self.rlan2[11][4] = 0.00408951
        self.rlan2[12][4] = 0.00396793
        self.rlan2[13][4] = 0.00363712

        self.rlan2[0][5] = 2.00 * 0.00001
        self.rlan2[1][5] = 7.10 * 0.00001
        self.rlan2[2][5] = 19.70 * 0.00001
        self.rlan2[3][5] = 43.80 * 0.00001
        self.rlan2[4][5] = 81.10 * 0.00001
        self.rlan2[5][5] = 130.70 * 0.00001
        self.rlan2[6][5] = 157.40 * 0.00001
        self.rlan2[7][5] = 185.70 * 0.00001
        self.rlan2[8][5] = 215.10 * 0.00001
        self.rlan2[9][5] = 251.20 * 0.00001
        self.rlan2[10][5] = 284.60 * 0.00001
        self.rlan2[11][5] = 275.70 * 0.00001
        self.rlan2[12][5] = 252.30 * 0.00001
        self.rlan2[13][5] = 203.90 * 0.00001
    
        self.bet2[0][0] = -0.7494824600
        self.bet2[1][0] = 0.0108080720
        self.bet2[2][0] = 0.0940103059
        self.bet2[3][0] = 0.5292641686
        self.bet2[4][0] = 0.2186262218
        self.bet2[5][0] = 0.9583027845
        self.bet2[6][0] = -0.2880424830
        self.bet2[7][0] = -0.1908113865

        self.bet2[0][1] = -0.3457169653
        self.bet2[1][1] = 0.0334703319
        self.bet2[2][1] = 0.2672530336
        self.bet2[3][1] = 0.1822121131
        self.bet2[4][1] = 0.0000000000
        self.bet2[5][1] = 0.4757242578
        self.bet2[6][1] = -0.1119411682
        self.bet2[7][1] = 0.0000000000

        self.bet2[0][2] = -0.7494824600
        self.bet2[1][2] = 0.0108080720
    
        self.bet2[2][2] = 0.0940103059
        self.bet2[3][2] = 0.5292641686
        self.bet2[4][2] = 0.2186262218
        self.bet2[5][2] = 0.9583027845
    
        self.bet2[6][2] = -0.2880424830
        self.bet2[7][2] = -0.1908113865
    
        

        for i in range(6,12):
            self.bet2[0][i] = 0.00000000000000
            self.bet2[1][i] = 0.00000000000000
            self.bet2[2][i] = 0.07499257592975
            self.bet2[3][i] = 0.55263612260619
            self.bet2[4][i] = 0.27638268294593
            self.bet2[5][i] = 0.79185633720481
            self.bet2[6][i] = 0.00000000000000
            self.bet2[7][i] = 0.00000000000000



        self.rf2[0][0] = 0.5788413
        self.rf2[1][0] = 0.5788413
        self.rf2[0][1] = 0.72949880
        self.rf2[1][1] = 0.74397137
        self.rf2[0][2] = 0.5788413
        self.rf2[1][2] = 0.5788413
        self.rf2[0][3] = 1.0
        self.rf2[1][3] = 1.0
        self.rf2[0][4] = 1.0
        self.rf2[1][4] = 1.0
        self.rf2[0][5] = 1.0
        self.rf2[1][5] = 1.0

        

        for i in range(6,12):
            self.rf2[0][i] = 0.47519806426735
            self.rf2[1][i] = 0.50316401683903


        self.rf2[0][12] = 1.0
        self.rf2[1][12] = 1.0

        self.rlan2[0][6] = 0.000004059636
        self.rlan2[1][6] = 0.000045944465
        self.rlan2[2][6] = 0.000188279352
        self.rlan2[3][6] = 0.000492930493
        self.rlan2[4][6] = 0.000913603501
        self.rlan2[5][6] = 0.001471537353
        self.rlan2[6][6] = 0.001421275482
        self.rlan2[7][6] = 0.001970946494
        self.rlan2[8][6] = 0.001674745804
        self.rlan2[9][6] = 0.001821581075
        self.rlan2[10][6] = 0.001834477198
        self.rlan2[11][6] = 0.001919911972
        self.rlan2[12][6] = 0.002233371071
        self.rlan2[13][6] = 0.002247315779
        self.rmu2[0][6] = 0.000210649076
        self.rmu2[1][6] = 0.000192644865
        self.rmu2[2][6] = 0.000244435215
        self.rmu2[3][6] = 0.000317895949
        self.rmu2[4][6] = 0.000473261994
        self.rmu2[5][6] = 0.000800271380
        self.rmu2[6][6] = 0.001217480226
        self.rmu2[7][6] = 0.002099836508
        self.rmu2[8][6] = 0.003436889186
        self.rmu2[9][6] = 0.006097405623
        self.rmu2[10][6] = 0.010664526765
        self.rmu2[11][6] = 0.020148678452
        self.rmu2[12][6] = 0.037990796590
        self.rmu2[13][6] = 0.098333900733


        

        self.rlan2[0][7] = 0.000000000001
        self.rlan2[1][7] = 0.000099483924
        self.rlan2[2][7] = 0.000287041681
        self.rlan2[3][7] = 0.000545285759
        self.rlan2[4][7] = 0.001152211095
        self.rlan2[5][7] = 0.001859245108
        self.rlan2[6][7] = 0.002606291272
        self.rlan2[7][7] = 0.003221751682
        self.rlan2[8][7] = 0.004006961859
        self.rlan2[9][7] = 0.003521715275
        self.rlan2[10][7] = 0.003593038294
        self.rlan2[11][7] = 0.003589303081
        self.rlan2[12][7] = 0.003538507159
        self.rlan2[13][7] = 0.002051572909

        

        self.rmu2[0][7] = 0.000173593803
        self.rmu2[1][7] = 0.000295805882
        self.rmu2[2][7] = 0.000228322534
        self.rmu2[3][7] = 0.000363242389
        self.rmu2[4][7] = 0.000590633044
        self.rmu2[5][7] = 0.001086079485
        self.rmu2[6][7] = 0.001859999966
        self.rmu2[7][7] = 0.003216600974
        self.rmu2[8][7] = 0.004719402141
        self.rmu2[9][7] = 0.008535331402
        self.rmu2[10][7] = 0.012433511681
        self.rmu2[11][7] = 0.020230197885
        self.rmu2[12][7] = 0.037725498348
        self.rmu2[13][7] = 0.106149118663


        

        self.rlan2[0][8] = 0.000007500161
        self.rlan2[1][8] = 0.000081073945
        self.rlan2[2][8] = 0.000227492565
        self.rlan2[3][8] = 0.000549786433
        self.rlan2[4][8] = 0.001129400541
        self.rlan2[5][8] = 0.001813873795
        self.rlan2[6][8] = 0.002223665639
        self.rlan2[7][8] = 0.002680309266
        self.rlan2[8][8] = 0.002891219230
        self.rlan2[9][8] = 0.002534421279
        self.rlan2[10][8] = 0.002457159409
        self.rlan2[11][8] = 0.002286616920
        self.rlan2[12][8] = 0.001814802825
        self.rlan2[13][8] = 0.001750879130

        self.rmu2[0][8] = 0.000229120979
        self.rmu2[1][8] = 0.000262988494
        self.rmu2[2][8] = 0.000314844090
        self.rmu2[3][8] = 0.000394471908
        self.rmu2[4][8] = 0.000647622610
        self.rmu2[5][8] = 0.001170202327
        self.rmu2[6][8] = 0.001809380379
        self.rmu2[7][8] = 0.002614170568
        self.rmu2[8][8] = 0.004483330681
        self.rmu2[9][8] = 0.007393665092
        self.rmu2[10][8] = 0.012233059675
        self.rmu2[11][8] = 0.021127058106
        self.rmu2[12][8] = 0.037936954809
        self.rmu2[13][8] = 0.085138518334

        self.rlan2[0][9] = 0.000045080582
        self.rlan2[1][9] = 0.000098570724
        self.rlan2[2][9] = 0.000339970860
        self.rlan2[3][9] = 0.000852591429
        self.rlan2[4][9] = 0.001668562761
        self.rlan2[5][9] = 0.002552703284
        self.rlan2[6][9] = 0.003321774046
        self.rlan2[7][9] = 0.005373001776
        self.rlan2[8][9] = 0.005237808549
        self.rlan2[9][9] = 0.005581732512
        self.rlan2[10][9] = 0.005677419355
        self.rlan2[11][9] = 0.006513409962
        self.rlan2[12][9] = 0.003889457523
        self.rlan2[13][9] = 0.002949061662

        self.rmu2[0][9] = 0.000563507269
        self.rmu2[1][9] = 0.000369640217
        self.rmu2[2][9] = 0.001019912579
        self.rmu2[3][9] = 0.001234013911
        self.rmu2[4][9] = 0.002098344078
        self.rmu2[5][9] = 0.002982934175
        self.rmu2[6][9] = 0.005402445702
        self.rmu2[7][9] = 0.009591474245
        self.rmu2[8][9] = 0.016315472607
        self.rmu2[9][9] = 0.020152229069
        self.rmu2[10][9] = 0.027354838710
        self.rmu2[11][9] = 0.050446998723
        self.rmu2[12][9] = 0.072262026612
        self.rmu2[13][9] = 0.145844504021


        

        self.rlan2[0][10] = 0.000000000001
        self.rlan2[1][10] = 0.000071525212
        self.rlan2[2][10] = 0.000288799028
        self.rlan2[3][10] = 0.000602250698
        self.rlan2[4][10] = 0.000755579402
        self.rlan2[5][10] = 0.000766406354
        self.rlan2[6][10] = 0.001893124938
        self.rlan2[7][10] = 0.002365580107
        self.rlan2[8][10] = 0.002843933070
        self.rlan2[9][10] = 0.002920921732
        self.rlan2[10][10] = 0.002330395655
        self.rlan2[11][10] = 0.002036291235
        self.rlan2[12][10] = 0.001482683983
        self.rlan2[13][10] = 0.001012248203


        

        self.rmu2[0][10] = 0.000465500812
        self.rmu2[1][10] = 0.000600466920
        self.rmu2[2][10] = 0.000851057138
        self.rmu2[3][10] = 0.001478265376
        self.rmu2[4][10] = 0.001931486788
        self.rmu2[5][10] = 0.003866623959
        self.rmu2[6][10] = 0.004924932309
        self.rmu2[7][10] = 0.008177071806
        self.rmu2[8][10] = 0.008638202890
        self.rmu2[9][10] = 0.018974658371
        self.rmu2[10][10] = 0.029257567105
        self.rmu2[11][10] = 0.038408980974
        self.rmu2[12][10] = 0.052869579345
        self.rmu2[13][10] = 0.074745721133



        

        self.rlan2[0][11] = 0.000012355409
        self.rlan2[1][11] = 0.000059526456
        self.rlan2[2][11] = 0.000184320831
        self.rlan2[3][11] = 0.000454677273
        self.rlan2[4][11] = 0.000791265338
        self.rlan2[5][11] = 0.001048462801
        self.rlan2[6][11] = 0.001372467817
        self.rlan2[7][11] = 0.001495473711
        self.rlan2[8][11] = 0.001646746198
        self.rlan2[9][11] = 0.001478363563
        self.rlan2[10][11] = 0.001216010125
        self.rlan2[11][11] = 0.001067663700
        self.rlan2[12][11] = 0.001376104012
        self.rlan2[13][11] = 0.000661576644

        self.rmu2[0][11] = 0.000212632332
        self.rmu2[1][11] = 0.000242170741
        self.rmu2[2][11] = 0.000301552711
        self.rmu2[3][11] = 0.000369053354
        self.rmu2[4][11] = 0.000543002943
        self.rmu2[5][11] = 0.000893862331
        self.rmu2[6][11] = 0.001515172239
        self.rmu2[7][11] = 0.002574669551
        self.rmu2[8][11] = 0.004324370426
        self.rmu2[9][11] = 0.007419621918
        self.rmu2[10][11] = 0.013251765130
        self.rmu2[11][11] = 0.022291427490
        self.rmu2[12][11] = 0.041746550635
        self.rmu2[13][11] = 0.087485802065

    def CalculateAbsoluteRisk(self,CurrentAge,ProjectionAge,AgeIndicator,NumberOfBiopsy,MenarcheAge,FirstLiveBirthAge,FirstDegRelatives,EverHadBiopsy,ihyp,rhyp,irace):
        return self.CalculateRisk(1
            , CurrentAge
            , ProjectionAge
            , AgeIndicator
            , NumberOfBiopsy
            , MenarcheAge
            , FirstLiveBirthAge
            , EverHadBiopsy
            , FirstDegRelatives
            , ihyp
            , rhyp
            , irace
            )

    def CalculateAeverageRisk(self,CurrentAge,ProjectionAge,AgeIndicator,NumberOfBiopsy,MenarcheAge,FirstLiveBirthAge,FirstDegRelatives,EverHadBiopsy,ihyp,rhyp,irace):
        return self.CalculateRisk(2
            , CurrentAge
            , ProjectionAge
            , AgeIndicator
            , NumberOfBiopsy
            , MenarcheAge
            , FirstLiveBirthAge
            , EverHadBiopsy
            , FirstDegRelatives
            , ihyp
            , rhyp
            , irace
            )

    def CalculateRisk(self,riskindex,CurrentAge,ProjectionAge,AgeIndicator,NumberOfBiopsy,MenarcheAge,FirstLiveBirthAge,EverHadBiopsy,FirstDegRelatives,ihyp,rhyp,irace):
        retval = 0.0
        abss = 0.0
        r8iTox2 = [[0 for i in range(9)] for j in range(216)]
        
        n = 216
        r = 0.0
        
        ni = 0
        ns = 0
        ti = float(CurrentAge)
        ts = float(ProjectionAge)

        
        for i in range(0,8):
            self.bet[i] = self.bet2[i][irace - 1]

        if (irace == 2):
            if (MenarcheAge == 2):
                MenarcheAge = 1
                FirstLiveBirthAge = 0
        for i in range(1,16):
            if (ti < self.t[i - 1]):
                ni = i - 1
                break

        for i in range(1,16):
            if (ts <= self.t[i - 1]):
                ns = i - 1
                break
        incr = 0
        if (riskindex == 2 and irace < 7):
            incr = 3

        cindx = incr + irace - 1

        for i in range(0,14):
            self.rmu[i] = self.rmu2[i][cindx]
            self.rlan[i] = self.rlan2[i][cindx]


        self.rf[0] = self.rf2[0][incr + irace - 1]
        self.rf[1] = self.rf2[1][incr + irace - 1]
        if (riskindex == 2 and irace >= 7):
            self.rf[0] = self.rf2[0][12]
            self.rf[1] = self.rf2[1][12]


        if (riskindex >= 2):
            MenarcheAge = 0
            NumberOfBiopsy = 0
            FirstLiveBirthAge = 0
            FirstDegRelatives = 0
            rhyp = 1.0

        ilev = AgeIndicator * 108 + MenarcheAge * 36 + NumberOfBiopsy * 12 + FirstLiveBirthAge * 3 + FirstDegRelatives + 1

        for k in range(0,216):
            r8iTox2[k][0] = 1.0

        for k in range(0,108):
            r8iTox2[k][1] = 0.0
            r8iTox2[108 + k][1] = 1.0

        for j in range(1,3):
            for k in range(1,37):
                r8iTox2[(j - 1) * 108 + k - 1][2] = 0.0
                r8iTox2[(j - 1) * 108 + 36 + k - 1][2] = 1.0
                r8iTox2[(j - 1) * 108 + 72 + k - 1][2] = 2.0

        for j in range(1,7):
            for k in range(1,13):
                r8iTox2[(j - 1) * 36 + k - 1][3] = 0.0
                r8iTox2[(j - 1) * 36 + 12 + k - 1][3] = 1.0
                r8iTox2[(j - 1) * 36 + 24 + k - 1][3] = 2.0

        for j in range(1,19):
            for k in range(1,4):
                r8iTox2[(j - 1) * 12 + k - 1][4] = 0.0
                r8iTox2[(j - 1) * 12 + 3 + k - 1][4] = 1.0
                r8iTox2[(j - 1) * 12 + 6 + k - 1][4] = 2.0
                r8iTox2[(j - 1) * 12 + 9 + k - 1][4] = 3.0

        for j in range(1,73):
            r8iTox2[(j - 1) * 3 + 1 - 1][5] = 0.0
            r8iTox2[(j - 1) * 3 + 2 - 1][5] = 1.0
            r8iTox2[(j - 1) * 3 + 3 - 1][5] = 2.0

        for i in range(0,216):
            r8iTox2[i][6] = r8iTox2[i][1] * r8iTox2[i][3]
            r8iTox2[i][7] = r8iTox2[i][4] * r8iTox2[i][5]

        for i in range(0,216):
            r8iTox2[i][8] = 1.0

        for i in range(0,216):
            self.sumb[i] = 0.0
            for j in range(0,8):
                self.sumb[i] += self.bet[j] * r8iTox2[i][j]

        for i in range(1,109):
            self.sumbb[i - 1] = self.sumb[i - 1] - self.bet[0]
        
        for i in range(109,217):
            self.sumbb[i - 1] = self.sumb[i - 1] - self.bet[0] - self.bet[1]
        
        for j in range(1,7):
            self.rlan[j - 1] *= self.rf[0]
        
        for j in range(7,15):
            self.rlan[j - 1] *= self.rf[1]
        
        i = ilev

        self.sumbb[i - 1] += math.log(rhyp)
        if (i <= 108):
            self.sumbb[i + 107] += math.log(rhyp)

        if (ts <= self.t[ni]):
            self.abs[i - 1] = 1.0 - math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1]) * (ts - ti))
            self.abs[i - 1] = self.abs[i - 1] * self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) / (self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1])
        else:
            self.abs[i - 1] = 1.0 - math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1]) * (self.t[ni] - ti))
            self.abs[i - 1] = self.abs[i - 1] * self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) / (self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1])
            
            if (ns - ni > 0):
                if (float(ProjectionAge) > 50.0 and float(CurrentAge) < 50.0):
                    r = 1.0 - math.exp(-(self.rlan[ns - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[ns - 1]) * (ts - self.t[ns - 1]))
                    r = r * self.rlan[ns - 1] * math.exp(self.sumbb[i + 107]) / (self.rlan[ns - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[ns - 1])
                    r *= math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1]) * (self.t[ni] - ti))

                    if (ns - ni > 1):
                        MenarcheAge = ns - 1
                        for j in range(ni + 1,MenarcheAge+1):
                            if (self.t[j - 1] >= 50.0):
                                r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[j - 1]) * (self.t[j] - self.t[j - 1]))
                            else:
                                r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[j - 1]) * (self.t[j]- self.t[j - 1]))
                    self.abs[i - 1] += r
                else:
                    r = 1.0 - math.exp(-(self.rlan[ns - 1] * math.exp(self.sumbb[i - 1])+ self.rmu[ns - 1]) * (ts - self.t[ns - 1]))
                    r = r * self.rlan[ns - 1] * math.exp(self.sumbb[i - 1]) / (self.rlan[ns - 1] * math.exp(self.sumbb[i - 1]) +self.rmu[ns - 1])
                    r *= math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1]) * (self.t[ni] - ti))
                    if (ns - ni > 1):
                        MenarcheAge = ns - 1
                        for j in range(ni + 1,MenarcheAge+1):
                            r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[j - 1]) * (self.t[j] - self.t[j - 1]))
                    self.abs[i - 1] += r

            if (ns - ni > 1):
                if (float(ProjectionAge) > 50.0 and float(CurrentAge) < 50.0):
                    MenarcheAge = ns - 1
                    for k in range(ni + 1,MenarcheAge+1):
                        if (self.t[k - 1] >= 50.0):
                            r = 1.0 - math.exp(-(self.rlan[k - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[k - 1]) * (self.t[k] -self.t[k - 1]))
                            r = r * self.rlan[k - 1] * math.exp(self.sumbb[i + 107]) / (self.rlan[k - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[k - 1])
                        else:
                            r = 1.0 - math.exp(-(self.rlan[k - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[k - 1]) * (self.t[k] -self.t[k - 1]))
                            r = r * self.rlan[k - 1] * math.exp(self.sumbb[i - 1]) / (self.rlan[k - 1] * math.exp(self.sumbb[i -1]) + self.rmu[k - 1])
                        r *= math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[ni - 1]) * (self.t[ni] - ti))
                        NumberOfBiopsy = k - 1

                        for j in range(ni + 1,NumberOfBiopsy+1):
                            if (self.t[j - 1] >= 50.0):
                                r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i + 107]) + self.rmu[j - 1]) * (self.t[j] - self.t[j - 1]))
                            else:
                                r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[j - 1]) * (self.t[j]- self.t[j - 1]))
                        self.abs[i - 1] += r
                else:
                    MenarcheAge = ns - 1
                    for k in range(ni + 1,MenarcheAge+1):
                        r = 1.0 - math.exp(-(self.rlan[k - 1] * math.exp(self.sumbb[i - 1]) + self.rmu[k - 1]) * (self.t[k] - self.t[k - 1]))
                        r = r * self.rlan[k - 1] * math.exp(self.sumbb[i - 1]) /(self.rlan[k - 1] * math.exp(self.sumbb[i - 1]) +  self.rmu[k - 1])
                        r *= math.exp(-(self.rlan[ni - 1] * math.exp(self.sumbb[i - 1])  + self.rmu[ni - 1]) * (self.t[ni] - ti))
                        NumberOfBiopsy = k - 1
                        for j in range(ni + 1,NumberOfBiopsy+1):
                            r *= math.exp(-(self.rlan[j - 1] * math.exp(self.sumbb[i -1]) + self.rmu[j - 1]) * (self.t[j] - self.t[j - 1]))
                        self.abs[i - 1] += r

        abss = self.abs[i - 1] * 1000.0
        
        if (abss - int(abss) >= .5):
            abss = int(abss) + 1.0
        else:
            abss = int(abss)

        abss /= 10.0

        retval = self.abs[i - 1]
        return retval
