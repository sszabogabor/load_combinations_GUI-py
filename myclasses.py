'''
Created on 25.4.2014, 6.2015

@author: gabors
'''

import sys
import logging
from wx import wx
import wx.xrc
import wx.dataview


#set up logging
logging.basicConfig(filename='logfile.log',filemode='w',level=logging.DEBUG,format='%(asctime)s %(message)s')

#string format variables
if sys.platform.startswith("linux"):
    s_bold="\033[1m"
    s_uline="\033[4m"
    s_end="\033[0m"
else:
    s_bold=""
    s_uline=""
    s_end=""

#global variables
LGcount=0
LCcount=0
LCInCom=0


class LoadCase:
    """Load case representig loads

    :param str loadCaseName: string
    :param str memberOfLoadGroup: string
    """
    loadCaseName=None
    loadCaseDescription=None
    memberOfLoadGroup=None
    loadCaseMatrix=None

    def __init__(self,loadCaseName="LC1",loadCaseDescription="",memberOfLoadGroup=None,loadCaseMatrix=[]):
        self.loadCaseName=loadCaseName
        self.loadCaseDescription=loadCaseDescription
        self.memberOfLoadGroup=memberOfLoadGroup
        self.loadCaseMatrix=loadCaseMatrix

    def change(self,loadCaseName=None,loadCaseDescription=None,memberOfLoadGroup=None,loadCaseMatrix=None):
        self.loadCaseName=loadCaseName
        self.loadCaseDescription=loadCaseDescription
        self.memberOfLoadGroup=memberOfLoadGroup


class LoadGroup:
    """Load group representing a group of load

    with specific properties
    TODO if load case is permanent can't be exclusive
    """
    loadGroupName=None
    loadGroupDescription=None
    loadGroupType=None              #standard, exclusive
    loadGroupActing=None            #permanent load, variable load,
    loadGroupLoadFactorFav=None
    loadGroupLoadFactorUnfav=None
    loadGroupCombinationFactorPsi0=None
    loadGroupCombinationFactorPsi1=None
    loadGroupCombinationFactorPsi2=None
    loadGroupContainedLoadCases=None


    def __init__(self,loadGroupName="LG1",loadGroupDescription="",loadGroupType="Standard",loadGroupActing="Permanent",loadGroupLoadFactorUnfav=1.35,loadGroupLoadFactorFav=1.00,loadGroupCombinationFactorPsi0=1.0,loadGroupCombinationFactorPsi1=1.0,loadGroupCombinationFactorPsi2=1.0,loadGroupContainedLoadCases=[]):
        self.loadGroupName=loadGroupName
        self.loadGroupDescription=loadGroupDescription
        self.loadGroupType=loadGroupType
        self.loadGroupActing=loadGroupActing
        self.loadGroupLoadFactorFav=loadGroupLoadFactorFav
        self.loadGroupLoadFactorUnfav=loadGroupLoadFactorUnfav
        self.loadGroupCombinationFactorPsi0=loadGroupCombinationFactorPsi0
        self.loadGroupCombinationFactorPsi1=loadGroupCombinationFactorPsi1
        self.loadGroupCombinationFactorPsi2=loadGroupCombinationFactorPsi2
        self.loadGroupContainedLoadCases=loadGroupContainedLoadCases

    def change(self,loadGroupName=None,loadGroupDescription=None,loadGroupType=None,loadGroupActing=None,loadGroupLoadFactorUnfav=None,loadGroupLoadFactorFav=None,loadGroupCombinationFactorPsi0=None,loadGroupCombinationFactorPsi1=None,loadGroupCombinationFactorPsi2=None,loadGroupContainedLoadCases=None):
        self.loadGroupName=loadGroupName
        self.loadGroupDescription=loadGroupDescription
        self.loadGroupType=loadGroupType
        self.loadGroupActing=loadGroupActing
        self.loadGroupLoadFactorFav=loadGroupLoadFactorFav
        self.loadGroupLoadFactorUnfav=loadGroupLoadFactorUnfav
        self.loadGroupCombinationFactorPsi0=loadGroupCombinationFactorPsi0
        self.loadGroupCombinationFactorPsi1=loadGroupCombinationFactorPsi1
        self.loadGroupCombinationFactorPsi2=loadGroupCombinationFactorPsi2
        self.loadGroupContainedLoadCases=loadGroupContainedLoadCases

    def __iter__(self):
        return iter(self.__list)


class LinearCombination:
    """Linear combination

    with specific properties without PSI factors for variable load cases

    :param dir linearCombinationIncludedLoadCases: dir of LC-s objects
    returns Combination key for all internal forces max or min
    """
    linearCombinationName=None
    linearCombinationDescription=None
    loadCasesIntoLComb=None

    def __init__(self,linearCombinationName="LCO1",linearCombinationDescription="",loadCasesIntoLComb=[]):
        self.linearCombinationName=linearCombinationName
        self.linearCombinationDescription=linearCombinationDescription
        self.loadCasesIntoLComb=loadCasesIntoLComb

    def change(self,linearCombinationName=None,linearCombinationDescription=None,loadCasesIntoLComb=None):
        self.linearCombinationName=linearCombinationName
        self.linearCombinationDescription=linearCombinationDescription
        self.loadCasesIntoLComb=loadCasesIntoLComb

    def makeCombination(self,extreme):  #extreme max or min
        #print included combinations list
        strTemp=""
        for i in self.loadCasesIntoLComb:
                strTemp += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName+",")
                #strTemp += (i.loadCaseName+",")
        print("Included load cases in linear combination:"+ strTemp[0:(len(strTemp)-1)])
        frame.textToOutput("Included load cases in linear combination:"+ strTemp[0:(len(strTemp)-1)])

        #main iteration for all internal forces
        for internalForce in [0,1,2]:
            tempVarloadcases={"Variable_Standard":[]} #dir contains variable LC + the extrem of Exclusive Variable LC
            #string storing combination key
            combKey=""
            combVal=0
            # work out if there is any exclusive load groups and make lists for them
            for i in self.loadCasesIntoLComb:
                #find out load case is in which load group
                loadGroupIndex=lookupForLoadGroupNumByName(loadCases[lookupForLoadCaseNumByName(i)].memberOfLoadGroup)
                #permanent load cases are processes immediately and are added into combkey variable
                #if i.memberOfLoadGroup.loadGroupActing == "Permanent":
                if loadGroups[loadGroupIndex].loadGroupActing == "Permanent":
                    #condition for max and min and determining favorable and unfavorable internal forces - Permanent load cases
                    if extreme == "max":
                        if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+s_end+ "+")
                            combVal = combVal + loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                        else:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+"+")
                            combVal = combVal + loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    elif extreme == "min":
                        if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+"+")
                            combVal = combVal + loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                        else:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" +s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+"+")
                            combVal = combVal + loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    else:
                        print("Something is wrong with argument extreme: max min (permanent load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (permanent load cases)")
                #variable load cases are sorted by properties "standard" or "Exclusive"
                elif loadGroups[loadGroupIndex].loadGroupActing == "Variable":
                    #Standard load cases are stored in dir tempVarloadcases under "Variable_standard" key
                    if loadGroups[loadGroupIndex].loadGroupType == "Standard":
                        tempVarloadcases.get("Variable_Standard").append(loadCases[lookupForLoadCaseNumByName(i)])
                    #exclusive load cases are stored in dir tempVarloadcases under loadGroupName key
                    elif loadGroups[loadGroupIndex].loadGroupType == "Exclusive":
                        if tempVarloadcases.get(loadGroups[loadGroupIndex].loadGroupName)==None:
                            tempVarloadcases[loadGroups[loadGroupIndex].loadGroupName]=[loadCases[lookupForLoadCaseNumByName(i)]]
                        else:
                            tempVarloadcases.get(loadGroups[loadGroupIndex].loadGroupName).append(loadCases[lookupForLoadCaseNumByName(i)])
                else:
                    print("Something is wrong with load case Type assignments")
                    frame.textToOutput("Something is wrong with load case Type assignments")
            #searching the extreme loadcase from exclusives for loadGroup
            for i in tempVarloadcases:
                tempValueMax=None
                tempLCMax=None
                if i!="Variable_Standard":
                    if extreme == "max":
                        for j in tempVarloadcases[i]:
                            loadGroupIndex=lookupForLoadGroupNumByName(j.memberOfLoadGroup)
                            if tempValueMax==None:
                                tempValueMax=j.loadCaseMatrix[internalForce]
                                tempLCMax=j
                            else:
                                if tempValueMax<j.loadCaseMatrix[internalForce]:
                                    tempValueMax=j.loadCaseMatrix[internalForce]
                                    tempLCMax=j
                                else:
                                    tempValueMax=tempValueMax
                        # the extreme loadcase from variable cases is added into Variable_Standard list
                        tempVarloadcases.get("Variable_Standard").append(tempLCMax)
                    if extreme == "min":
                        for j in tempVarloadcases[i]:
                            loadGroupIndex=lookupForLoadGroupNumByName(j.memberOfLoadGroup)
                            if tempValueMax==None:
                                tempValueMax=j.loadCaseMatrix[internalForce]
                                tempLCMax=j
                            else:
                                if tempValueMax>j.loadCaseMatrix[internalForce]:
                                    tempValueMax=j.loadCaseMatrix[internalForce]
                                    tempLCMax=j
                                else:
                                    tempValueMax=tempValueMax
                        # the extreme loadcase from variable cases is added into Variable_Standard list
                        tempVarloadcases.get("Variable_Standard").append(tempLCMax)

            #condition for max and min and determining favorable and unfavorable internal forces - Variable load cases with extremes from Exclusives LC
            for i in tempVarloadcases.get("Variable_Standard"):
                loadGroupIndex=lookupForLoadGroupNumByName(i.memberOfLoadGroup)
                if extreme == "max":
                    if i.loadCaseMatrix[internalForce]>0:
                        combKey += (i.loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+"+")
                        combVal = combVal + i.loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                    else:
                        combKey += (i.loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+"+")
                        combVal = combVal + i.loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                elif extreme == "min":
                    if i.loadCaseMatrix[internalForce]<=0:
                        combKey += (i.loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+"+")
                        combVal = combVal + i.loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                    else:
                        combKey += (i.loadCaseName + "*" + s_bold+str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+"+")
                        combVal = combVal + i.loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                else:
                    print("Something is wrong with argument extreme: max min (Variable load cases)")
                    frame.textToOutput("Something is wrong with argument extreme: max min (Variable load cases)")
            #the output of the combination key and the combination value
            if extreme == "max":
                print("Combination key (max) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                frame.textToOutput("Combination key (max) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                print("Result (max) for internal force labelled as '"+ str(internalForce) +"': " +  str(combVal))
                frame.textToOutput("Result (max) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
            elif extreme == "min":
                print("Combination key (min) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                frame.textToOutput("Combination key (min) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                print("Result (min) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
                frame.textToOutput("Result (min) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
            else:
                print("Something is wrong with argument extreme: max min (print com bkey)")
                frame.textToOutput("Something is wrong with argument extreme: max min (print com bkey)")

class CombinationMSU:
    """combination

    with specific properties with PSI factors for variable load cases ---- See EN 1990, 6.4.3.2 (6.10)

    :param dir linearCombinationIncludedLoadCases: dir of LC-s objects
    returns Combination key for all internal forces max or min
    """
    linearCombinationName=None
    linearCombinationDescription=None
    loadCasesIntoComb=None


    def __init__(self,linearCombinationName="CO1",linearCombinationDescription="",loadCasesIntoComb=[]):
        self.linearCombinationName=linearCombinationName
        self.linearCombinationDescription=linearCombinationDescription
        self.loadCasesIntoComb=loadCasesIntoComb

    def change(self,linearCombinationName=None,linearCombinationDescription=None,loadCasesIntoComb=None):
        self.linearCombinationName=linearCombinationName
        self.linearCombinationDescription=linearCombinationDescription
        self.loadCasesIntoComb=loadCasesIntoComb

    def makeCombination(self,extreme):  #extreme max or min

        #print included combinations list
        strTemp=""
        for i in self.loadCasesIntoComb:
                #strTemp += (i.loadCaseName+",")
                strTemp += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName+",")
        print("Included load cases in combination MSU:"+ strTemp[0:(len(strTemp)-1)])
        frame.textToOutput("Included load cases in combination MSU:"+ strTemp[0:(len(strTemp)-1)])

        #main iteration for all internal forces
        for internalForce in [0,1,2]:
            tempVarloadcases={"Variable_Standard":[]} #dir contains variable LC + the extrem of Exclusive Variable LC
            #string storing combination key
            combKey=""
            combVal=0
            # work out if there is any exclusive load groups and make lists for them
            for i in self.loadCasesIntoComb:
                #find out load case is in which load group
                loadGroupIndex=lookupForLoadGroupNumByName(loadCases[lookupForLoadCaseNumByName(i)].memberOfLoadGroup)
                #permanent load cases are processes immediately and are added into combkey variable
                if loadGroups[loadGroupIndex].loadGroupActing == "Permanent":
                    #condition for max and min and determining favorable and unfavorable internal forces - Permanent load cases
                    if extreme == "max":
                        if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end + "+")
                            combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                        else:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end + "+")
                            combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    elif extreme == "min":
                        if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end + "+")
                            combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                        else:
                            combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end + "+")
                            combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    else:
                        print("Something is wrong with argument extreme: max min (permanent load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (permanent load cases)")

                #variable load cases are sorted by properties "standard" or "Exclusive"
                elif loadGroups[loadGroupIndex].loadGroupActing == "Variable":
                    #Standard load cases are stored in dir tempVarloadcases under "Variable_standard" key
                    if loadGroups[loadGroupIndex].loadGroupType == "Standard":
                        tempVarloadcases.get("Variable_Standard").append(i)
                    #exclusive load cases are stored in dir tempVarloadcases under loadGroupName key
                    elif loadGroups[loadGroupIndex].loadGroupType == "Exclusive":
                        if tempVarloadcases.get(loadGroups[loadGroupIndex].loadGroupName)==None:
                            tempVarloadcases[loadGroups[loadGroupIndex].loadGroupName]=[i]
                        else:
                            tempVarloadcases.get(loadGroups[loadGroupIndex].loadGroupName).append(i)
                else:
                    print("Something is wrong with load case Type assignments")
                    frame.textToOutput("Something is wrong with load case Type assignments")
            #searching the extreme loadcase from exclusives for loadGroup
            for i in tempVarloadcases:
                tempValueMax=None
                tempLCMax=None
                if i!="Variable_Standard":
                    if extreme == "max":
                        for j in tempVarloadcases[i]:
                            if tempValueMax==None:
                                tempValueMax=loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]
                                tempLCMax=j
                            else:
                                if tempValueMax<loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]:
                                    tempValueMax=loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]
                                    tempLCMax=j
                                else:
                                    tempValueMax=tempValueMax
                        # the extreme loadcase from variable cases is added into Variable_Standard list
                        tempVarloadcases.get("Variable_Standard").append(tempLCMax)
                    elif extreme == "min":
                        for j in tempVarloadcases[i]:
                            if tempValueMax==None:
                                tempValueMax=loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]
                                tempLCMax=j
                            else:
                                if tempValueMax>loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]:
                                    tempValueMax=loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]
                                    tempLCMax=j
                                else:
                                    tempValueMax=tempValueMax
                        # the extreme loadcase from variable cases is added into Variable_Standard list
                        tempVarloadcases.get("Variable_Standard").append(tempLCMax)

            #work out leading load case

            isLeadingLoadCase=None
            theExtreme=0
            for i in tempVarloadcases.get("Variable_Standard"):
                if isLeadingLoadCase==None:
                    isLeadingLoadCase=i
                    if extreme == "max":
                        for j in tempVarloadcases.get("Variable_Standard"):
                            loadGroupIndex=lookupForLoadGroupNumByName(loadCases[lookupForLoadCaseNumByName(j)].memberOfLoadGroup)
                            if loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]>0:
                                if i==j:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                                else:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            elif loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]<=0:
                                if i==j:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                                else:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            else:
                                print("Something is wrong with argument extreme: max min (variable standard load cases)")
                                frame.textToOutput("Something is wrong with argument extreme: max min (variable standard load cases)")
                    elif extreme == "min":
                        for j in tempVarloadcases.get("Variable_Standard"):
                            if loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]>0:
                                if i==j:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                                else:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            elif loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]<=0:
                                if i==j:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                                else:
                                    theExtreme += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            else:
                                print("Something is wrong with argument extreme: max min (variable standard load cases)")
                                frame.textToOutput("Something is wrong with argument extreme: max min (variable standard load cases)")
                    else:
                        print ("Something is wrong with argument extreme: max min (variable standard load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (variable standard load cases)")
                else:
                    if extreme == "max":
                        theExtreme_temp=0
                        for j in tempVarloadcases.get("Variable_Standard"):
                            if loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]>0:
                                if i==j:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                                else:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            elif loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]<=0:
                                if i==j:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                                else:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            else:
                                print("Something is wrong with argument extreme: max min (permanent load cases)")
                                frame.textToOutput("Something is wrong with argument extreme: max min (permanent load cases)")
                    elif extreme == "min":
                        theExtreme_temp=0
                        for j in tempVarloadcases.get("Variable_Standard"):
                            if loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]>0:
                                if i==j:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                                else:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            elif loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]<=0:
                                if i==j:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                                else:
                                    theExtreme_temp += loadCases[lookupForLoadCaseNumByName(j)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                            else:
                                print("Something is wrong with argument extreme: max min (variable standard load cases)")
                                frame.textToOutput("Something is wrong with argument extreme: max min (variable standard load cases)")
                    else:
                        print("Something is wrong with argument extreme: max min (variable standard load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (variable standard load cases)")
                        #assign the extremem load case
                    if extreme == "max":
                        if theExtreme_temp>theExtreme:
                            isLeadingLoadCase=j
                    elif extreme == "min":
                        if theExtreme_temp<=theExtreme:
                            isLeadingLoadCase=j
                    else:
                        print ("Something is wrong with max min")
                        frame.textToOutput("Something is wrong with max min")

            #condition for max and min and determining favorable and unfavorable internal forces - Variable load cases with extremes from Exclusives LC
            for i in tempVarloadcases.get("Variable_Standard"):
                loadGroupIndex=lookupForLoadGroupNumByName(loadCases[lookupForLoadCaseNumByName(i)].memberOfLoadGroup)
                if extreme == "max":
                    if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0 and i!=isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+ "*" + s_uline+str(loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0) + s_end + "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0 and i==isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+ "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0 and i!=isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+ "*" + s_uline+str(loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0) + s_end + "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0 and i==isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+ "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    else:
                        print("Something is wrong with argument extreme: max min (Variable load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (Variable load cases)")
                elif extreme == "min":
                    if loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0 and i!=isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+ "*" + s_uline+str(loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0) + s_end + "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]<=0 and i==isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav)+ s_end+ "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorUnfav
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0 and i!=isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+ "*" + s_uline+str(loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0) + s_end + "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav*loadGroups[loadGroupIndex].loadGroupCombinationFactorPsi0
                    elif loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]>0 and i==isLeadingLoadCase:
                        combKey += (loadCases[lookupForLoadCaseNumByName(i)].loadCaseName + "*" + s_bold + str(loadGroups[loadGroupIndex].loadGroupLoadFactorFav)+ s_end+ "+")
                        combVal +=  loadCases[lookupForLoadCaseNumByName(i)].loadCaseMatrix[internalForce]*loadGroups[loadGroupIndex].loadGroupLoadFactorFav
                    else:
                        print("Something is wrong with argument extreme: max min (Variable load cases)")
                        frame.textToOutput("Something is wrong with argument extreme: max min (Variable load cases)")
                else:
                    print("Something is wrong with argument extreme: max min (Variable load cases)")
                    frame.textToOutput("Something is wrong with argument extreme: max min (Variable load cases)")
            #the output of the combination key and the combination value
            if extreme == "max":
                print("Combination key (max) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                frame.textToOutput("Combination key (max) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                print("Result (max) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
                frame.textToOutput("Result (max) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
            elif extreme == "min":
                print("Combination key (min) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                frame.textToOutput("Combination key (min) for internal force labelled as '"+ str(internalForce) +"': " + combKey[0:(len(combKey)-1)])
                print("Result (min) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
                frame.textToOutput("Result (min) for internal force labelled as '"+ str(internalForce) +"': " + str(combVal))
            else:
                print("Something is wrong with argument extreme: max min (print com bkey)")
                frame.textToOutput("Something is wrong with argument extreme: max min (print com bkey)")



class MyFrame2 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Combination Input Table", pos = wx.DefaultPosition, size = wx.Size( 1020,1135 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.Size( 1010,910 ), wx.Size( -1,-1 ) )

        self.m_statusBar2 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )

        gbSizer1 = wx.GridBagSizer( 0, 0 )
        gbSizer1.SetFlexibleDirection( wx.BOTH )
        gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        gbSizer2 = wx.GridBagSizer( 0, 0 )
        gbSizer2.SetFlexibleDirection( wx.BOTH )
        gbSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"Input Load Groups", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        self.m_staticText10.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

        gbSizer2.Add( self.m_staticText10, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"LoadGroupName", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )

        gbSizer2.Add( self.m_staticText16, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, u"LG_my", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl4, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"LoadGroupDescription", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )

        gbSizer2.Add( self.m_staticText14, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl5 = wx.TextCtrl( self, wx.ID_ANY, u"MyDescription", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl5, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, u"LoadGroupType", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )

        gbSizer2.Add( self.m_staticText15, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        m_choice1Choices = [ u"Standard", u"Exclusive" ]
        self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        self.m_choice1.SetSelection( 0 )
        self.m_choice1.Enable( False )

        gbSizer2.Add( self.m_choice1, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText18 = wx.StaticText( self, wx.ID_ANY, u"LoadGroupActing", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText18.Wrap( -1 )

        gbSizer2.Add( self.m_staticText18, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        m_choice2Choices = [ u"Permanent", u"Variable" ]
        self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
        self.m_choice2.SetSelection( 0 )

        gbSizer2.Add( self.m_choice2, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, u"LoadFactorFav", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )

        gbSizer2.Add( self.m_staticText19, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, u"1.35", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl8, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, u"LoadFactorUnfav", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )

        gbSizer2.Add( self.m_staticText20, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl9 = wx.TextCtrl( self, wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl9, wx.GBPosition( 6, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, u"CombinationFactorPsi0", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )

        gbSizer2.Add( self.m_staticText21, wx.GBPosition( 7, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl10 = wx.TextCtrl( self, wx.ID_ANY, u"0.75", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl10, wx.GBPosition( 7, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, u"CombinationFactorPsi1", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText22.Wrap( -1 )

        gbSizer2.Add( self.m_staticText22, wx.GBPosition( 8, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl11 = wx.TextCtrl( self, wx.ID_ANY, u"0.4", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl11, wx.GBPosition( 8, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"CombinationFactorPsi1", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText23.Wrap( -1 )

        gbSizer2.Add( self.m_staticText23, wx.GBPosition( 9, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl12 = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer2.Add( self.m_textCtrl12, wx.GBPosition( 9, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer1.Add( gbSizer2, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

        self.m_dataViewListCtrl1 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 730,-1 ), wx.dataview.DV_ROW_LINES )
        self.m_dataViewListColumn1 = self.m_dataViewListCtrl1.AppendTextColumn( u"Name" , width=150)
        self.m_dataViewListColumn2 = self.m_dataViewListCtrl1.AppendTextColumn( u"Description" , width=150)
        self.m_dataViewListColumn3 = self.m_dataViewListCtrl1.AppendTextColumn( u"Type" )
        self.m_dataViewListColumn4 = self.m_dataViewListCtrl1.AppendTextColumn( u"Acting" )
        self.m_dataViewListColumn5 = self.m_dataViewListCtrl1.AppendTextColumn( u"gamma sup")
        self.m_dataViewListColumn6 = self.m_dataViewListCtrl1.AppendTextColumn( u"gamma inf" )
        self.m_dataViewListColumn7 = self.m_dataViewListCtrl1.AppendTextColumn( u"psi 0" , width=40)
        self.m_dataViewListColumn8 = self.m_dataViewListCtrl1.AppendTextColumn( u"psi 1" , width=40)
        self.m_dataViewListColumn9 = self.m_dataViewListCtrl1.AppendTextColumn( u"psi 2" , width=40)
        gbSizer1.Add( self.m_dataViewListCtrl1, wx.GBPosition( 0, 1 ), wx.GBSpan( 2, 1 ), wx.ALL|wx.EXPAND, 5 )

        gbSizer7 = wx.GridBagSizer( 0, 0 )
        gbSizer7.SetFlexibleDirection( wx.BOTH )
        gbSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button3 = wx.Button( self, wx.ID_ANY, u"Add", wx.Point( -1,-1 ), wx.Size( 70,-1 ), 0 )

        gbSizer7.Add( self.m_button3, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button31 = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )

        gbSizer7.Add( self.m_button31, wx.GBPosition( 0, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button5 = wx.Button( self, wx.ID_ANY, u"Change", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
        self.m_button5.SetToolTipString( u"Row must be selected" )

        gbSizer7.Add( self.m_button5, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer1.Add( gbSizer7, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

        gbSizer11 = wx.GridBagSizer( 0, 0 )
        gbSizer11.SetFlexibleDirection( wx.BOTH )
        gbSizer11.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Input Load Cases", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        self.m_staticText11.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

        gbSizer11.Add( self.m_staticText11, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"LoadCaseName", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )

        gbSizer11.Add( self.m_staticText25, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl13 = wx.TextCtrl( self, wx.ID_ANY, u"LC_my", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer11.Add( self.m_textCtrl13, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"LoadCaseDescription", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )

        gbSizer11.Add( self.m_staticText26, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl14 = wx.TextCtrl( self, wx.ID_ANY, u"MyDescription", wx.DefaultPosition, wx.DefaultSize, 0 )

        gbSizer11.Add( self.m_textCtrl14, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"MemberOfLoadGroup", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText27.Wrap( -1 )

        gbSizer11.Add( self.m_staticText27, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        m_choice3Choices = []
        self.m_choice3 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )
        self.m_choice3.SetSelection( 0 )

        gbSizer11.Add( self.m_choice3, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, u"LoadCaseMatrix", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )

        gbSizer11.Add( self.m_staticText28, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl15 = wx.TextCtrl( self, wx.ID_ANY, u"15,-3,5", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl15.SetToolTipString( u"Example:5,-3,2" )

        gbSizer11.Add( self.m_textCtrl15, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer1.Add( gbSizer11, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

        self.m_dataViewListCtrl4 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_ROW_LINES)
        self.m_dataViewListColumn10 = self.m_dataViewListCtrl4.AppendTextColumn( u"Name" , width=200)
        self.m_dataViewListColumn11 = self.m_dataViewListCtrl4.AppendTextColumn( u"Description" , width=200)
        self.m_dataViewListColumn12 = self.m_dataViewListCtrl4.AppendTextColumn( u"Member of load group", width=200 )
        self.m_dataViewListColumn13 = self.m_dataViewListCtrl4.AppendTextColumn( u"Matrix" )

        gbSizer1.Add( self.m_dataViewListCtrl4, wx.GBPosition( 2, 1 ), wx.GBSpan( 2, 1 ), wx.ALL|wx.EXPAND, 5 )

        gbSizer9 = wx.GridBagSizer( 0, 0 )
        gbSizer9.SetFlexibleDirection( wx.BOTH )
        gbSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button6 = wx.Button( self, wx.ID_ANY, u"Change", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
        self.m_button6.SetToolTipString( u"Row must be selected" )

        gbSizer9.Add( self.m_button6, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button4 = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )

        gbSizer9.Add( self.m_button4, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button7 = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )

        gbSizer9.Add( self.m_button7, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        gbSizer1.Add( gbSizer9, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

        gbSizer13 = wx.GridBagSizer( 0, 0 )
        gbSizer13.SetFlexibleDirection( wx.BOTH )
        gbSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_dataViewListCtrl3 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 470,200 ), 0 )
        self.m_dataViewListColumn15 = self.m_dataViewListCtrl3.AppendTextColumn( u"Load Cases", width=450)
        gbSizer13.Add( self.m_dataViewListCtrl3, wx.GBPosition( 1, 0 ), wx.GBSpan( 4, 1 ), wx.ALL, 5 )

        self.m_dataViewListCtrl41 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 470,200 ), 0 )
        self.m_dataViewListColumn16 = self.m_dataViewListCtrl41.AppendTextColumn( u"Incl.LoadCases" , width=450)
        gbSizer13.Add( self.m_dataViewListCtrl41, wx.GBPosition( 1, 2 ), wx.GBSpan( 4, 1 ), wx.ALL, 5 )

        self.m_button21 = wx.Button( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        gbSizer13.Add( self.m_button21, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button22 = wx.Button( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        gbSizer13.Add( self.m_button22, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_staticText33 = wx.StaticText( self, wx.ID_ANY, u"LoadCases", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText33.Wrap( -1 )
        gbSizer13.Add( self.m_staticText33, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText34 = wx.StaticText( self, wx.ID_ANY, u"LC's in combin.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText34.Wrap( -1 )
        gbSizer13.Add( self.m_staticText34, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button12 = wx.Button( self, wx.ID_ANY, u">>", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        self.m_button12.SetToolTipString( u"Add all" )

        gbSizer13.Add( self.m_button12, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button13 = wx.Button( self, wx.ID_ANY, u"<<", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        self.m_button13.SetToolTipString( u"Remove all" )

        gbSizer13.Add( self.m_button13, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer13.AddGrowableRow( 0 )
        gbSizer13.AddGrowableRow( 1 )
        gbSizer13.AddGrowableRow( 2 )

        gbSizer1.Add( gbSizer13, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 2 ), wx.EXPAND, 5 )

        gbSizer12 = wx.GridBagSizer( 0, 0 )
        gbSizer12.SetFlexibleDirection( wx.BOTH )
        gbSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        gbSizer12.SetEmptyCellSize( wx.Size( -1,0 ) )

        self.m_button9 = wx.Button( self, wx.ID_ANY, u"Read from file", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer12.Add( self.m_button9, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"MakeULSCombination", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button8.SetToolTipString( u"First save the project\nthen reopen it\nAfter that you can do the combinations" )

        gbSizer12.Add( self.m_button8, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText32 = wx.StaticText( self, wx.ID_ANY, u"Combination rules:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText32.Wrap( -1 )
        self.m_staticText32.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

        gbSizer12.Add( self.m_staticText32, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALIGN_BOTTOM|wx.ALL, 5 )

        self.m_textCtrl111 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 1000,200 ), wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
        gbSizer12.Add( self.m_textCtrl111, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )

        self.m_button10 = wx.Button( self, wx.ID_ANY, u"MakeLinearCombination", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button10.SetToolTipString( u"First save the project\nthen reopen it\nAfter that you can do the combinations" )

        gbSizer12.Add( self.m_button10, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        gbSizer1.Add( gbSizer12, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 2 ), wx.EXPAND, 5 )


        self.SetSizer( gbSizer1 )
        self.Layout()
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.AppendItem( self.m_menuItem1 )

        self.m_menuItem2 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Save", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.AppendItem( self.m_menuItem2 )

        self.m_menubar1.Append( self.m_menu1, u"File" )

        self.SetMenuBar( self.m_menubar1 )


        self.Centre( wx.BOTH )

        # Connect Events
        self.m_choice2.Bind( wx.EVT_UPDATE_UI, self.setLGTypeAccordingActing )
        self.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.LC_Sel, id = self.m_dataViewListCtrl4.GetId() )
        self.m_button3.Bind( wx.EVT_BUTTON, self.AddLoadGroup )
        self.m_button31.Bind( wx.EVT_BUTTON, self.DeleteLoadGroup )
        self.m_button5.Bind( wx.EVT_BUTTON, self.ChangeLoadGroup )
        self.m_textCtrl15.Bind( wx.EVT_LEAVE_WINDOW, self.checkInputNumsCommas )
        self.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.LG_Sel, id = self.m_dataViewListCtrl1.GetId() )
        self.m_button6.Bind( wx.EVT_BUTTON, self.ChangeLoadCase )
        self.m_button21.Bind( wx.EVT_BUTTON, self.addToCombination )
        self.m_button22.Bind( wx.EVT_BUTTON, self.removeFromCombination )
        self.m_button12.Bind( wx.EVT_BUTTON, self.addToCombinationAll )
        self.m_button13.Bind( wx.EVT_BUTTON, self.removeFromCombinationAll )
        self.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.addToCombination, id = self.m_dataViewListCtrl3.GetId() )
        self.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.removeFromCombination, id = self.m_dataViewListCtrl41.GetId() )
        self.m_button4.Bind( wx.EVT_BUTTON, self.AddLoadCase )
        self.m_button7.Bind( wx.EVT_BUTTON, self.DeleteLoadCase )
        self.m_button9.Bind( wx.EVT_BUTTON, self.readFromFile )
        self.m_button8.Bind( wx.EVT_BUTTON, self.callMakeULSComb )
        self.m_button10.Bind( wx.EVT_BUTTON, self.callMakeLinComb )
        self.Bind( wx.EVT_MENU, self.readFromFile, id = self.m_menuItem1.GetId() )
        self.Bind( wx.EVT_MENU, self.writeToFile, id = self.m_menuItem2.GetId() )

    def __del__( self ):
        pass

    # Virtual event handlers, overide them in your derived class

    def setLGTypeAccordingActing( self, event ):
        if self.m_choice2.CurrentSelection==0:
            self.m_choice1.Disable()
            self.m_choice1.SetSelection(0)
        else:
            self.m_choice1.Enable()

        event.Skip()


    def DeleteLoadGroup( self, event ):
        # deleting load group influenced the wxChoice object
        if self.m_dataViewListCtrl1.GetSelectedRow() != -1:
            # first delete the item from choice object
            #temp=self.m_dataViewListCtrl1.GetSelectedRow()
            self.m_choice3.Delete(self.m_choice3.FindString(str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),0))))
            # now the row from ListCtrl can be deleted
            self.m_dataViewListCtrl1.DeleteItem(self.m_dataViewListCtrl1.GetSelectedRow())
            global LGcount
            LGcount -=1
            self.writeStatusBar()
        event.Skip()

    def AddLoadGroup( self, event ):
        self.m_dataViewListCtrl1.AppendItem([self.m_textCtrl4.Value,self.m_textCtrl5.Value,self.m_choice1.GetString(self.m_choice1.CurrentSelection),self.m_choice2.GetString(self.m_choice2.CurrentSelection),self.m_textCtrl8.Value,self.m_textCtrl9.Value,self.m_textCtrl10.Value,self.m_textCtrl11.Value,self.m_textCtrl12.Value])
        self.m_choice3.Append(self.m_textCtrl4.Value)
        global LGcount
        LGcount +=1
        self.writeStatusBar()
        event.Skip()

    def ChangeLoadGroup( self, event ):
        # first delete the item from choice object
        self.m_choice3.Delete(self.m_choice3.FindString(str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),0))))

        #make changes
        #LG name
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl4.Value,self.m_dataViewListCtrl1.GetSelectedRow(),0)
        #LG description
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl5.Value,self.m_dataViewListCtrl1.GetSelectedRow(),1)
        #LG type
        #self.m_choice1.SetString=0
        self.m_dataViewListCtrl1.SetTextValue(self.m_choice1.GetString(self.m_choice1.CurrentSelection),self.m_dataViewListCtrl1.GetSelectedRow(),2)
        #LG acting
        self.m_dataViewListCtrl1.SetTextValue(self.m_choice2.GetString(self.m_choice2.CurrentSelection),self.m_dataViewListCtrl1.GetSelectedRow(),3)
        #LG LoadFactorFav
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl8.Value,self.m_dataViewListCtrl1.GetSelectedRow(),4)
        #LG LoadFactorUnFav
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl9.Value,self.m_dataViewListCtrl1.GetSelectedRow(),5)
        #LG LoadFactorpsi0
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl10.Value,self.m_dataViewListCtrl1.GetSelectedRow(),6)
        #LG LoadFactorpsi1
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl11.Value,self.m_dataViewListCtrl1.GetSelectedRow(),7)
        #LG LoadFactorpsi2
        self.m_dataViewListCtrl1.SetTextValue(self.m_textCtrl12.Value,self.m_dataViewListCtrl1.GetSelectedRow(),8)

        #then append the new name of load group
        self.m_choice3.Append(self.m_textCtrl4.Value)

        event.Skip()

    #get data from selected row and put it into textctr
    def LG_Sel( self, event ):
        #LG name
        self.m_textCtrl4.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),0))
        #LG description
        self.m_textCtrl5.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),1))
        #LG type
        #self.m_choice1.SetString=0
        #self.m_textCtrl5.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),2))
        #LG acting
        #self.m_textCtrl5.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),3))
        #LG LoadFactorFav
        self.m_textCtrl8.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),4))
        #LG LoadFactorUnFav
        self.m_textCtrl9.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),5))
        #LG LoadFactorpsi0
        self.m_textCtrl10.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),6))
        #LG LoadFactorpsi1
        self.m_textCtrl11.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),7))
        #LG LoadFactorpsi2
        self.m_textCtrl12.Value=str(self.m_dataViewListCtrl1.GetTextValue(self.m_dataViewListCtrl1.GetSelectedRow(),8))

        event.Skip()

    def DeleteLoadCase( self, event ):
        if self.m_dataViewListCtrl4.GetSelectedRow() != -1:
            #store the selected row number for deleting in combination LC window
            temp=self.m_dataViewListCtrl4.GetSelectedRow()
            self.m_dataViewListCtrl4.DeleteItem(self.m_dataViewListCtrl4.GetSelectedRow())
            #delete name from combination LC window
            self.m_dataViewListCtrl3.DeleteItem(temp)
            global LCcount
            LCcount  -=1
            self.writeStatusBar()
        event.Skip()

    def AddLoadCase( self, event ):
        #add item to main LC window
        self.m_dataViewListCtrl4.AppendItem([self.m_textCtrl13.Value,self.m_textCtrl14.Value,self.m_choice3.GetString(self.m_choice3.CurrentSelection),self.m_textCtrl15.Value])
        #add item to combination LC window
        self.m_dataViewListCtrl3.AppendItem([self.m_textCtrl13.Value])
        global LCcount
        LCcount  +=1
        #add Load case to the loadCases list where every load case is present, problem is with changing
        #loadCases.append(LoadCase(self.m_textCtrl13.Value,self.m_textCtrl14.Value,self.m_choice3.GetString(self.m_choice3.CurrentSelection),[[float(self.m_textCtrl15.Value.split(",")[1]),float(self.m_textCtrl15.Value.split(",")[2]),float(self.m_textCtrl15.Value.split(",")[3].rstrip())]]))
        self.writeStatusBar()
        event.Skip()

    def ChangeLoadCase( self, event ):
        #make changes
        #LC name
        self.m_dataViewListCtrl4.SetTextValue(self.m_textCtrl13.Value,self.m_dataViewListCtrl4.GetSelectedRow(),0)
        #LC description
        self.m_dataViewListCtrl4.SetTextValue(self.m_textCtrl14.Value,self.m_dataViewListCtrl4.GetSelectedRow(),1)
        #LC included load group
        self.m_dataViewListCtrl4.SetTextValue(self.m_choice3.GetString(self.m_choice3.CurrentSelection),self.m_dataViewListCtrl4.GetSelectedRow(),2)
        #LC matrix
        self.m_dataViewListCtrl4.SetTextValue(self.m_textCtrl15.Value,self.m_dataViewListCtrl4.GetSelectedRow(),3)
        #change name in combinatin LC window
        self.m_dataViewListCtrl3.SetTextValue(self.m_textCtrl13.Value,self.m_dataViewListCtrl4.GetSelectedRow(),0)
        event.Skip()

    def LC_Sel( self, event ):
        #LC name
        self.m_textCtrl13.Value=str(self.m_dataViewListCtrl4.GetTextValue(self.m_dataViewListCtrl4.GetSelectedRow(),0))
        #LC description
        self.m_textCtrl14.Value=str(self.m_dataViewListCtrl4.GetTextValue(self.m_dataViewListCtrl4.GetSelectedRow(),1))
        #LC matrix
        self.m_textCtrl15.Value=str(self.m_dataViewListCtrl4.GetTextValue(self.m_dataViewListCtrl4.GetSelectedRow(),3))

        event.Skip()

    def writeStatusBar(self):
        self.m_statusBar2.SetStatusText("LoadGroupCount:" + str( LGcount)+"; " + "LoadCaseCount:" + str( LCcount))


    def writeToFile( self, event ):
        #prepare text o write to file and call function to write it
        output_list=[]
        output_line="1,"
        #Load Group
        for pom in range(LGcount):
            for i in range(9):
                output_line += self.m_dataViewListCtrl1.GetTextValue(pom,i) + ","
            pom += pom
            print(output_line[:len(output_line)-1])
            #self.textToFile("data1111.txt",output_line[:len(output_line)-1])
            #add the output line to a list output

            ####
            #There is a problem that the internal forces
            ####


            output_list.append(output_line[:len(output_line)-1])
            output_line="1,"
        #Load Case
        output_line="2,"
        for pom in range(LCcount):
            for i in range(4):
                output_line += self.m_dataViewListCtrl4.GetTextValue(pom,i) + ","
            pom += pom
            print(output_line[:len(output_line)-1])
            #self.textToFile("data1111.txt",output_line[:len(output_line)-1])
            output_list.append(output_line[:len(output_line)-1])
            output_line="2,"

        #added LG count
        output_list.append("LGcount"+str(LGcount))

        #added LC count
        output_list.append("LCcount"+str(LCcount))


        fname=self.OnSaveAs()
        self.textToFile(fname,output_list)

        event.Skip()

    def readFromFile( self, event ):

        # if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
        #                wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #    return

        # else: proceed asking to the user the new file to open
        #clear output txtcontrol, list of LGs and LCs
        self.m_textCtrl111.Clear()
        self.m_dataViewListCtrl1.DeleteAllItems()
        self.m_dataViewListCtrl4.DeleteAllItems()
        self.m_dataViewListCtrl3.DeleteAllItems()
        self.m_dataViewListCtrl41.DeleteAllItems()

        #reset ounters
        global LCInCom
        LCInCom=0
        #reset loadGroups
        global loadGroups
        loadGroups=[]
        #reset loadCases
        global loadCases
        loadCases=[]
        #reset load gropu choice
        self.m_choice3.Clear()

        openFileDialog = wx.FileDialog(self, "Open txt file", "", "","txt files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # proceed loading the file chosen by the user
        # this can be done with e.g. wxPython input streams:
        input_stream = openFileDialog.GetPath()

        #logging
        logging.info("Read data from file: " + openFileDialog.GetPath() )

        #read data from file myclasses, add new funcion
        ReadDataFileLines(input_stream)
        #write status bar
        self.writeStatusBar()


#      if not input_stream.IsOk():
#          wx.LogError("Cannot open file '%s'."%openFileDialog.GetPath())
#          return

        event.Skip()


    def callMakeLinComb(self, event):
        #clear output window
        self.m_textCtrl111.Clear()
        #get list of LCs from dataViewListCtrl
        tempString="lcomb,CO1,MyDescription,"
        global LCInCom

        for pom in range(LCInCom):
            tempString += self.m_dataViewListCtrl41.GetTextValue(pom,0) + ","
        tempString=tempString[:len(tempString)-1]
        tempString=str(tempString)

        #the same code as in read from file
        pomNumbOfComas=tempString.count(",")
        pomLC=[]
        pomClear=tempString.rstrip()
        for i in range(pomNumbOfComas-2):
            pomLC.append(pomClear.split(",")[i+3])

        lincomb=LinearCombination(tempString.split(",")[1],tempString.split(",")[2],pomLC)
        lincomb.makeCombination("max")
        lincomb.makeCombination("min")


        event.Skip()

    def callMakeULSComb( self, event ):
        #clear output window
        self.m_textCtrl111.Clear()
        #get list of LCs from dataViewListCtrl
        tempString="combMSU,CO1,MyDescription,"
        global LCInCom

        for pom in range(LCInCom):
            tempString += self.m_dataViewListCtrl41.GetTextValue(pom,0) + ","
        tempString=tempString[:len(tempString)-1]
        tempString=str(tempString)

        #the same code as in read from file
        pomNumbOfComas=tempString.count(",")
        pomLC=[]
        pomClear=tempString.rstrip()
        for i in range(pomNumbOfComas-2):
            pomLC.append(pomClear.split(",")[i+3])

        comb=CombinationMSU(tempString.split(",")[1],tempString.split(",")[2],pomLC)
        comb.makeCombination("max")
        comb.makeCombination("min")

        event.Skip()

    def textToFile(self, filename,output_list):
        # write text to file
        fh = None
        try:
            fh = open(filename, "w")
            i=0
            for i in range(len(output_list)):
                fh.write(output_list[i]+"\n")
            return True

        except (IOError, OSError) as err:
            print(err)
        finally:
            if fh is not None:
                fh.close()

    def OnSaveAs(self):

        saveFileDialog = wx.FileDialog(self, "Save txt file", "", "","txt files (*.txt)|*.txt", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        output_stream=saveFileDialog.GetPath()
                    # = wx.FileOutputStream(saveFileDialog.GetPath())
        return output_stream

        if not output_stream.IsOk():
            wx.LogError("Cannot save current contents in file '%s'."%saveFileDialog.GetPath())
            return

    def textToOutput(self,text):
        self.m_textCtrl111.AppendText(text)
        self.m_textCtrl111.AppendText( '\n' )

    def addToCombination( self, event ):
        global LCInCom
        #add item from litstrl 3
        tempDuplication=False
        #check for duplication
        for pom in range(LCInCom):
            if self.m_dataViewListCtrl41.GetTextValue(pom,0) != self.m_dataViewListCtrl3.GetTextValue(self.m_dataViewListCtrl3.GetSelectedRow(),0):
                tempDuplication=False
            elif self.m_dataViewListCtrl41.GetTextValue(pom,0) == self.m_dataViewListCtrl3.GetTextValue(self.m_dataViewListCtrl3.GetSelectedRow(),0):
                tempDuplication=True
                break
            else:
                wx.LogError("Something is wrong with LC name check at adding to combination")
        if tempDuplication==False:
            self.m_dataViewListCtrl41.AppendItem([self.m_dataViewListCtrl3.GetTextValue(self.m_dataViewListCtrl3.GetSelectedRow(),0)])
            LCInCom +=1
        else:
            wx.MessageBox("Duplicated name, LC doesn't added to combination","Info")
        event.Skip()

    def removeFromCombination( self, event ):
        global LCInCom
        self.m_dataViewListCtrl41.DeleteItem(self.m_dataViewListCtrl41.GetSelectedRow())
        if LCInCom !=0:
            LCInCom -=1
        event.Skip()

    def addToCombinationAll( self, event ):
        global LCInCom
        for pom1 in range(LCcount):
        #add item from litstrl 3
            tempDuplication=False
            #check for duplication
            for pom in range(LCInCom):
                if self.m_dataViewListCtrl41.GetTextValue(pom,0) != self.m_dataViewListCtrl3.GetTextValue(pom1,0):
                    tempDuplication=False
                elif self.m_dataViewListCtrl41.GetTextValue(pom,0) == self.m_dataViewListCtrl3.GetTextValue(pom1,0):
                    tempDuplication=True
                    break
                else:
                    wx.LogError("Something is wrong with LC name check at adding to combination")
            if tempDuplication==False:
                self.m_dataViewListCtrl41.AppendItem([self.m_dataViewListCtrl3.GetTextValue(pom1,0)])
                LCInCom +=1
            else:
                wx.MessageBox("Duplicated name, LC doesn't added to combination","Info")
            event.Skip()

    def removeFromCombinationAll( self, event ):
        global LCInCom
        if LCInCom !=0:
            self.m_dataViewListCtrl41.DeleteAllItems()
            LCInCom =0
        event.Skip()

    def checkInputNumsCommas( self, event ):
        #if self.m_textCtrl15.Value.isnumeric():
        #    wx.MessageBox("ok")
        #else:
        #    wx.MessageBox("wrong input")
        event.Skip()

def readFromFileLoadGroup(inputline):
    isLoadGropuVacant=True
    pomLG=LoadGroup(inputline.split(",")[1],inputline.split(",")[2], inputline.split(",")[3], inputline.split(",")[4], float(inputline.split(",")[5]), float(inputline.split(",")[6]), float(inputline.split(",")[7]), float(inputline.split(",")[8]), float(inputline.split(",")[9].rstrip()), [])
    # lookup for loadgroup if it is present or not
    for pom in range(len(loadGroups)):
        if loadGroups[pom].loadGroupName==pomLG.loadGroupName:
            isLoadGropuVacant=False

    if isLoadGropuVacant==True:
        #add load group to load group list
        loadGroups.append(pomLG)
        frame.m_dataViewListCtrl1.AppendItem([inputline.split(",")[1],inputline.split(",")[2],inputline.split(",")[3],inputline.split(",")[4],float(inputline.split(",")[5]),float(inputline.split(",")[6]),float(inputline.split(",")[7]),float(inputline.split(",")[8]),float(inputline.split(",")[9].rstrip())])
        #add name to choice3
        frame.m_choice3.Append(inputline.split(",")[1])
        logging.info("Load gropu: " + pomLG.loadGroupName + " added with params.:" + getLGParams(pomLG.loadGroupName))
    else:
        logging.warning("Load group: " + pomLG.loadGroupName +" does not added due to name conflict")


def readFromFileLoadCase(inputline):
    isLoadCaseVacant=True
    isLoadGropuReadyForUse=False
    pomLC=LoadCase(inputline.split(",")[1],inputline.split(",")[2], inputline.split(",")[3], [float(inputline.split(",")[4]),float(inputline.split(",")[5]),float(inputline.split(",")[6].rstrip())])
    # lookup for loadgroup if it is present or not
    for pom in range(len(loadCases)):
        if loadCases[pom].loadCaseName==pomLC.loadCaseName:
            isLoadCaseVacant=False
    for pom1 in range(len(loadGroups)):
        if pomLC.memberOfLoadGroup==loadGroups[pom1].loadGroupName:
            isLoadGropuReadyForUse=True
            indexOFLoadGroupForNextUse=pom1

    if isLoadCaseVacant==True and isLoadGropuReadyForUse==True:
        loadCases.append(pomLC)
        #add LC to LCs to combination dataViewList
        frame.m_dataViewListCtrl3.AppendItem([inputline.split(",")[1]])
        #add LC to LCs dataViewList
        frame.m_dataViewListCtrl4.AppendItem([inputline.split(",")[1],inputline.split(",")[2],inputline.split(",")[3],inputline.split(",")[4]+','+inputline.split(",")[5]+','+inputline.split(",")[6].rstrip()])
        loadGroups[indexOFLoadGroupForNextUse].loadGroupContainedLoadCases.append(pomLC.loadCaseName)
        logging.info("Load case: " + pomLC.loadCaseName + " added with params.:" + getLCParams(pomLC.loadCaseName))

    else:
        if isLoadCaseVacant==False:
            logging.warning("Load case: " + pomLC.loadCaseName +" does not added due to name conflict")
        elif isLoadGropuReadyForUse==False:
            logging.warning("Load case: " + pomLC.loadCaseName +" does not added due to load group does not exists")

def readFromFileLcomb(inputline):
    pomNumbOfComas=inputline.count(",")
    pomLC=[]
    pomClear=inputline.rstrip()
    for i in range(pomNumbOfComas-2):
        pomLC.append(pomClear.split(",")[i+3])

    lincomb=LinearCombination(inputline.split(",")[1],inputline.split(",")[2],pomLC)
    lincomb.makeCombination("min")
    lincomb.makeCombination("max")

def readFromFileCombMsu(inputline):
    pomNumbOfComas=inputline.count(",")
    pomLC=[]
    pomClear=inputline.rstrip()
    for i in range(pomNumbOfComas-2):
        pomLC.append(pomClear.split(",")[i+3])

    comb=CombinationMSU(inputline.split(",")[1],inputline.split(",")[2],pomLC)
    comb.makeCombination("min")
    comb.makeCombination("max")


def lookupForLoadGroupNumByName(name):
    for pom in range(len(loadGroups)):
        if loadGroups[pom].loadGroupName==name:
            return pom

def lookupForLoadCaseNumByName(name):
    for pom in range(len(loadCases)):
        if loadCases[pom].loadCaseName==name:
            return pom

def getLCParams(name):
    pom=loadCases[lookupForLoadCaseNumByName(name)]
    return (pom.loadCaseName +","+ pom.loadCaseDescription + ","+ pom.memberOfLoadGroup) + ","+ str(pom.loadCaseMatrix[0])+ ","+ str(pom.loadCaseMatrix[1])+ ","+ str(pom.loadCaseMatrix[2])

def getLGParams(name):
    pom=loadGroups[lookupForLoadGroupNumByName(name)]
    return (pom.loadGroupName +","+ pom.loadGroupDescription +","+ pom.loadGroupType +","+ pom.loadGroupActing +","+ str(pom.loadGroupLoadFactorFav) +","+ str(pom.loadGroupLoadFactorUnfav) +","+ str(pom.loadGroupCombinationFactorPsi0) +","+ str(pom.loadGroupCombinationFactorPsi1) +","+ str(pom.loadGroupCombinationFactorPsi2))

#read input data from file
def ReadDataFileLines(filename):

    #filename = "data.txt"               #sys.argv[1]              #get filename from arguments after *.py file
    try:
        fin=None
        fin=open(filename)                #fin is file objects for reading

        for line in fin:                    #the file object is iterable so you can iterate like a sequence
            if not line.startswith("'"):    #exception for commented lines with '
                if line.startswith("1"):
                    readFromFileLoadGroup(line)
                elif line.startswith("2"):
                    readFromFileLoadCase(line)
                elif line.startswith("lcomb"):
                    readFromFileLcomb(line)
                elif line.startswith("combMSU"):
                    readFromFileCombMsu(line)
                elif line.startswith("LCcount"):
                    global LCcount
                    LCcount=int(line[7:])
                elif line.startswith("LGcount"):
                    global LGcount
                    LGcount=int(line[7:])

    except (IOError, OSError) as err:
        print(err)
    finally:
        if fin is not None:
            fin.close()

#### THE MANIN PART
#make a list of load groups
loadGroups=[]
#make a list of load cases
loadCases=[]
#make default LG
##LG1=LoadGroup()
#append the default loadGruop to the list of loadGroups
##loadGroups.append(LG1)
##logging.info("Default load group LG1 added with params.:" + getLGParams("LG1"))
#make default LC
##LC1=LoadCase(loadCaseDescription="DefaultLoadCase",memberOfLoadGroup="LG1",loadCaseMatrix=[-10,-5,457])
#append the default loadCase to the list of loadCases
#loadCases.append(LC1)
##logging.info("Default load case LC1 added with params.:" + getLCParams("LC1"))
##LG1.loadGroupContainedLoadCases.append("LC1")

app=wx.App(False)
frame=MyFrame2(None)
frame.Show(True)
app.MainLoop()
