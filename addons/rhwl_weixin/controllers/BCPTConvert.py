# -*- coding: utf-8 -*-

class BcptConvert():
    _White = 1
    _Black = 2
    _Hispanic = 3
    _AAChinese = 7
    _AAJapanese = 8
    _AAFilipino = 9
    _AAHawaiian = 10
    _AAOtherPacificIslander = 11
    _AAOtherAsianAmerican = 12
    _UNKNOWN = "UNKNOWN"
    _UDERSCORE = "__"
    _EMPTY = ""
    _YES = "YES"
    _NO = "NO"
    _NA = "NA"
    _0BIRTHS = "0 BIRTHS"


    def GetCurrentAge(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=90
        elif(str(o).upper() in ("< 35","<35")):
            rval=34
        else:
            rval=int(o)
        return rval

    def GetProjectionAge(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=90
        else:
            rval=int(o)
        return rval

    def GetMenarcheAge(self,o):
        val=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA,self._0BIRTHS)):
            rval=90
        elif(str(o).upper()=="7 TO 11"):
            rval = 10
        elif(str(o).upper()=="12 TO 13"):
            rval = 13
        elif(str(o).upper()=="> 13"):
            rval = 15
        else:
            rval=int(o)
        return rval

    def GetFirstLiveBirthAge(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=99
        elif(str(o).upper()=="NO BIRTHS"):
            rval = 0
        elif(str(o).upper()=="< 20"):
            rval = 15
        elif(str(o).upper()=="20 TO 24"):
            rval = 22
        elif(str(o).upper()=="25 TO 30"):
            rval = 27
        elif(str(o).upper()=="> 30"):
            rval = 31
        else:
            rval = int(o)
        return rval

    def GetFirstDegRelatives(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=99
        elif(str(o).upper()=="0"):
            rval = 0
        elif(str(o).upper()=="1"):
            rval = 1
        elif(str(o).upper()=="> 1"):
            rval = 2
        else:
            rval = int(o)
        return rval

    def GetEverHadBiopsy(self,o):
        rval = 99
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=99
        elif(str(o).upper() in (self._NO,"0")):
            rval = 0
        elif(str(o).upper() in (self._YES,"1")):
            rval = 1
        return rval


    def GetNumberOfBiopsy(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=99
        elif(str(o).upper()=="1"):
            rval = 1
        elif(str(o).upper()=="> 1"):
            rval = 2
        else:
            rval = int(o)
        return rval


    def GetHyperPlasia(self,o):
        rval=0
        if(str(o).upper() in (self._UNKNOWN,self._UDERSCORE,self._EMPTY,self._NA)):
            rval=99
        elif(str(o).upper()== self._NO):
            rval = 0
        elif(str(o).upper()==self._YES):
            rval = 1
        else:
            rval = int(o)
        return rval



    def GetRace(self,o):
        rval=0
        if(str(o).upper() in ("WHITE",self._UNKNOWN,"1","4")):
            rval = self._White
        elif(str(o).upper() in ("BLACK","2")):
            rval = self._Black
        elif(str(o).upper() in ("HISPANIC","3")):
            rval = self._Hispanic
        elif(str(o).upper()=="7"):
            rval = self._AAChinese
        elif(str(o).upper()=="8"):
            rval = self._AAJapanese
        elif(str(o).upper()=="9"):
            rval = self._AAFilipino
        elif(str(o).upper()=="10"):
            rval = self._AAHawaiian
        elif(str(o).upper()=="11"):
            rval = self._AAOtherPacificIslander
        elif(str(o).upper()=="12"):
            rval = self._AAOtherAsianAmerican
        else:
            rval = self._White
        return rval


    def CurrentAgeIndicator(self,currentAge):
        rval = 0;
        if (currentAge < 50):
            rval = 0
        elif (currentAge >= 50):
            rval = 1
        return rval


    def MenarcheAge(self, menarcheAge):
        rval = 0
        if (menarcheAge >= 7 and menarcheAge < 12):
            rval = 2
        elif (menarcheAge >= 12 and menarcheAge < 14):
            rval = 1
        elif (menarcheAge >= 14 and menarcheAge <= 39 or menarcheAge == 99):
            rval = 0
        return rval


    def FirstLiveBirthAge(self,firstLiveBirthAge):
        rval = 0
        if (firstLiveBirthAge == 0):
            rval = 2
        elif(firstLiveBirthAge > 0):
            if (firstLiveBirthAge < 20 or firstLiveBirthAge == 99):
                rval = 0
            elif (firstLiveBirthAge >= 20 and firstLiveBirthAge < 25):
                rval = 1
            elif (firstLiveBirthAge >= 25 and firstLiveBirthAge < 30):
                rval = 2
            elif (firstLiveBirthAge >= 30 and firstLiveBirthAge <= 55):
                rval = 3
        return rval


    def FirstDegRelatives1(self,firstDegRelatives):
        rval = 0;
        if (firstDegRelatives == 0 or firstDegRelatives == 99):
            rval = 0
        elif (firstDegRelatives == 1):
            rval = 1
        elif (firstDegRelatives >= 2 and firstDegRelatives <= 31):
            rval = 2
        return rval


    def FirstDegRelatives2(self,firstDegRelatives, race):
        rval = 0;
        if (firstDegRelatives == 0 or firstDegRelatives == 99):
            rval = 0
        elif (firstDegRelatives == 1):
            rval = 1
        elif (firstDegRelatives >= 2 and firstDegRelatives <= 31 and race < 7):
            rval = 2
        elif (firstDegRelatives >= 2 and race >= 7):
            rval = 1
        return rval

    def EverHadBiopsy(self,everHadBiopsy):
        rval = 0
        if(everHadBiopsy==99):
            rval = 0
        else:
            rval = everHadBiopsy
        return rval


    def NumberOfBiopsy(self,numberOfPreviousBiopsy, everHadBiopsy):
        rval = 0
        if (everHadBiopsy == 99):
            rval = 99
        elif (numberOfPreviousBiopsy == 0 or (numberOfPreviousBiopsy == 99 and everHadBiopsy == 99)):
            rval = 0
        elif (numberOfPreviousBiopsy == 1 or (numberOfPreviousBiopsy == 99 and everHadBiopsy == 1)):
            rval = 1
        elif (numberOfPreviousBiopsy > 1 and numberOfPreviousBiopsy <= 30):
            rval = 2
        return rval


    def Hyperplasia(self,hyperplasia,everHadBiopsy):
        rval=0
        if (everHadBiopsy == 0):
            rval = 99
        else:
            rval = hyperplasia

        return rval

    def RHyperplasia(self,hyperplasia,everHadBiopsy):
        rval=0.0
        if(hyperplasia==1):
            rval = 1.82
        elif(hyperplasia==0):
            rval = 0.93
        else:
            rval = 1.0
        return rval

