import os
import Routines
import Calculations

from ikobconfig import getConfigFromArgs

# This routine inspects the command line
# of the specified configuration file in a dictionary.
# if there is a problem the program finishes here.
config = getConfigFromArgs()
Project_filename = config['__filename__']  # nieuw automatisch toegevoegd config item.

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config['project']
paths_config = config['project']['paths']
skims_config = config['skims']
tvom_config = config['TVOM']

# Ophalen van instellingen
scenario = project_config['scenario']
Basedirectory = paths_config['base_directory']
Skimsdirectory = os.path.join (Basedirectory, 'skims')
os.makedirs ( Skimsdirectory, exist_ok=True )
print (Skimsdirectory)
motives = project_config['motives']
chains = project_config['chains']['use']
Hubname = project_config['chains']['name hub']
TVOMwork = tvom_config['work']
TVOMother = tvom_config['other']
variablecarcosts = skims_config['variablecarcosts']
kmcharge = skims_config['kmcharge']
variable_costs_no_car = skims_config['variable costs no car']
time_costs_no_car = skims_config['time costs no car']
daypart = skims_config['part of the day']
nocarcategory = ['NoCar', 'NoLicense']
#benader_kosten = skims_config['Transit kosten']['benaderen']['use']
Transitkmcosts = skims_config['Transit costs']['kmcosts']
startingfee = skims_config['Transit costs']['starting fee']
Parkingsearchfile = skims_config['parking search file']
Additional_costs = skims_config['additional costs']['use']
Additional_costsfile = skims_config['additional costs']['data-file']
Parking_costs = skims_config['parking costs']['use']
Parking_costsfile = skims_config['parking costs']['data-file']


if Additional_costs:
    Additional_costsfile=Additional_costsfile.replace('.csv','')
    Additional_costsmatrix = Routines.csvintlezen(Additional_costsfile , aantal_lege_regels=0)

# Fixed values
incomes =  ['low', 'middle low', 'middle high', 'high']

Transitkmcosts = float(Transitkmcosts)/100
startingfee = float(startingfee)/100
variablecarcosts = float(variablecarcosts)/100
Parkingsearchfile=Parkingsearchfile.replace('.csv','')
Parking_time_list = Routines.csvlezen (Parkingsearchfile, aantal_lege_regels=1)
print (Project_filename)
Projectdirectory = os.path.join (Basedirectory, Project_filename)
print (Projectdirectory)
os.makedirs ( Projectdirectory, exist_ok=True)
Gen_traveltime_directory = os.path.join (Basedirectory, 'Gen_traveltime_')
print (Gen_traveltime_directory)
os.makedirs ( Gen_traveltime_directory, exist_ok=True )

def Transitcostscalc(distance, Transitkmcosts, startingfee):
    flaf = float(distance)
    if flaf <= 0:
        return 0
    else :
        return flaf * Transitkmcosts + startingfee
    return 0

for ds in daypart:
    Inputdirectory = os.path.join(Skimsdirectory, ds)
    Outputdirectory = os.path.join (Gen_traveltime_directory, ds)
    os.makedirs(Outputdirectory, exist_ok=True)
    print (Outputdirectory)
    CarTimefilename = os.path.join(Inputdirectory, f'Car_Time')
    CarTimematrix = Routines.csvfloatlezen(CarTimefilename, aantal_lege_regels=0)
    Cardistancefilename = os.path.join(Inputdirectory, f'Car_Distance')
    Cardistancematrix = Routines.csvfloatlezen(Cardistancefilename, aantal_lege_regels=0)
    BikeTimefilename = os.path.join(Inputdirectory, f'Bike_Time')
    BikeTimematrix = Routines.csvfloatlezen (BikeTimefilename, aantal_lege_regels=0)
    TransitTimefilename = os.path.join(Inputdirectory, f'Transit_Time')
    TransitTimematrix = Routines.csvfloatlezen(TransitTimefilename, aantal_lege_regels=0)
    Transitdistancefilename = os.path.join(Inputdirectory, f'Transit_Distance')
    Transitdistancematrix = Routines.csvfloatlezen(Transitdistancefilename, aantal_lege_regels=0)
    if Parking_costs:
        Parking_costsfile = Parking_costsfile.replace ( '.csv', '' )
        Parking_costslist = Routines.csvintlezen ( Parking_costsfile, aantal_lege_regels=0 )
    else:
        Parking_costslist = Routines.lijstvolnullen ( len ( Transitdistancematrix ) )
    print ( Parking_costslist )

    if chains :
        PplusBikeTimefilename = os.path.join(Inputdirectory, f'PplusBike_{Hubname}_Time')
        PplusBikeTimematrix = Routines.csvfloatlezen(PplusBikeTimefilename, aantal_lege_regels=0)
        PplusBikedistancefilename = os.path.join(Inputdirectory, f'PplusBike_{Hubname}_Distance_Car')
        PplusBikedistancematrix = Routines.csvfloatlezen(PplusBikedistancefilename, aantal_lege_regels=0)
        PplusRDestinationsTimefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Destinations_Time')
        PplusRDestinationsTimematrix = Routines.csvfloatlezen(PplusRDestinationsTimefilename, aantal_lege_regels=0)
        PplusROriginTimefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Origin_Time')
        PplusROriginTimematrix = Routines.csvfloatlezen(PplusROriginTimefilename, aantal_lege_regels=0)
        PplusRDestinationsTransitdistancefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Destinations_Distance_Transit')
        PplusRDestinationsTransitdistancematrix = Routines.csvfloatlezen(PplusRDestinationsTransitdistancefilename, aantal_lege_regels=0)
        PplusRDestinationsCardistancefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Destinations_Distance_Car')
        PplusRDestinationsCardistancematrix = Routines.csvfloatlezen(PplusRDestinationsCardistancefilename, aantal_lege_regels=0)
        PplusROriginTransitdistancefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Origin_Distance_Transit')
        PplusROriginTransitdistancematrix = Routines.csvfloatlezen(PplusROriginTransitdistancefilename, aantal_lege_regels=0)
        PplusROriginCardistancefilename = os.path.join(Inputdirectory, f'PplusR_{Hubname}_Origin_Distance_Car')
        PplusROriginCardistancematrix = Routines.csvfloatlezen(PplusROriginCardistancefilename, aantal_lege_regels=0)



    print("Park Time matrix contains {} zones.".format(len(Parking_time_list)))
    number_zones_Time = len(CarTimematrix)
    print("CarTimematrix contains {} zones.".format(number_zones_Time))
    number_zones_distance = len(Cardistancematrix)
    print("Car-distancematrix contains {} zones.".format(number_zones_distance))
    if number_zones_distance != number_zones_Time:
        print("FOUT: Nomber of zones not equal!?")
        quit()
    number_zones = number_zones_Time

    #kostenmatrix

    print("Bezig kosten berekenen.")
    afmeting = len (Transitdistancematrix)
    KostenmatrixTransit =  [ [ Transitcostscalc(Transitdistancematrix[i][j], Transitkmcosts, startingfee,)
                            for j in range(afmeting) ]
                            for i in range(afmeting) ]
    if chains:
        KostenDestinationsPplusRTransit = [ [ Transitcostscalc(PplusRDestinationsTransitdistancematrix[i][j], Transitkmcosts, startingfee,)
                                for j in range(afmeting) ]
                                for i in range(afmeting) ]
        KostenOriginPplusRTransit = [ [ Transitcostscalc(PplusROriginTransitdistancematrix[i][j], Transitkmcosts, startingfee,)
                                for j in range(afmeting) ]
                                for i in range(afmeting) ]

    # Eerst de Bike:

    GGRskim = []
    number_zones_Bike = len (BikeTimematrix)
    for i in range (0,number_zones_Bike):
        GGRskim.append([])
        for j in range (0,number_zones_Bike):
            if BikeTimematrix[i][j]<180:
                GGRskim[i].append(int(BikeTimematrix [i][j]))
            else:
                GGRskim[i].append(9999)
        for j in range (number_zones_Bike, number_zones) :
            GGRskim[i].append ( 9999 )
    for i in range (number_zones_Bike, number_zones):
        GGRskim.append([])
        for j in range (0,number_zones) :
            GGRskim[i].append(9999)


    Outputfilename = os.path.join(Outputdirectory, 'Bike')
    Routines.csvwegschrijven(GGRskim,Outputfilename)

    for inc in incomes:
        GGRskim = []
        MultiplyingFactor = TVOMwork.get(inc)
        for i in range (0,number_zones):
            GGRskim.append([])
            for j in range (0,number_zones):
                totalTime = CarTimematrix[i][j] + round(float(Parking_time_list[i][1]) + float(Parking_time_list[j][2]))
                if Additional_costs:
                    GGRskim[i].append ( int ( totalTime + MultiplyingFactor * (Cardistancematrix[i][j] *
                                              (variablecarcosts + kmcharge) + Additional_costsmatrix[i][j]/100) +
                                              Parking_costslist[j]/100))
                else:
                    GGRskim[i].append(int(totalTime + MultiplyingFactor * (Cardistancematrix [i][j] *
                                      (variablecarcosts+kmcharge) + Parking_costslist[j]/100)))

        Outputfilename = os.path.join(Outputdirectory, f'Car_{inc}')
        Routines.csvwegschrijven(GGRskim, Outputfilename)


        #Dan het Transit
        GGRskim = []
        MultiplyingFactor = TVOMwork.get (inc)
        for i in range (0, number_zones):
            GGRskim.append([])
            for j in range (0, number_zones):
                if float(TransitTimematrix[i][j])>0.5:
                    Resultaat = float(TransitTimematrix [i][j]) + MultiplyingFactor * float(KostenmatrixTransit [i][j])
                    Resultaatint = int (Resultaat)
                    GGRskim[i].append(Resultaatint)
                else:
                    GGRskim[i].append(9999)

        Outputfilename = os.path.join(Outputdirectory, f'Transit_{inc}')
        Routines.csvwegschrijven(GGRskim,Outputfilename)

        #Dan geen Car (rijbewijs)
        for ncc in nocarcategory :
            GGRskim = []
            MultiplyingFactor = TVOMwork.get(inc)
            for i in range (0,number_zones):
                GGRskim.append([])
                for j in range (0,number_zones):
                    if CarTimematrix[i][j] < 7:
                        GGRskim[i].append(99999)
                    else:
                        totalTime = CarTimematrix[i][j] +round(float(Parking_time_list[i][1]) + float(Parking_time_list[j][2]))
                        totalKosten = CarTimematrix[i][j] * time_costs_no_car.get(ncc) + \
                                       Cardistancematrix[i][j] * (variable_costs_no_car.get(ncc) + kmcharge)
                        GGRskim[i].append(int(totalTime + MultiplyingFactor * totalKosten))

            Outputfilename = os.path.join(Outputdirectory, f'{ncc}_{inc}')
            Routines.csvwegschrijven(GGRskim, Outputfilename)

        # Nu FreeCar
        for inc in incomes:
            GGRskim = []
            MultiplyingFactor = TVOMwork.get ( inc )
            for i in range ( 0, number_zones ):
                GGRskim.append ( [] )
                for j in range ( 0, number_zones ):
                    totalTime = CarTimematrix[i][j] + round(float(Parking_time_list[i][1]) + float(Parking_time_list[j][2]))
                    if Additional_costs:
                        GGRskim[i].append ( int ( totalTime + MultiplyingFactor * Cardistancematrix[i][j] *
                                            kmcharge + Additional_costsmatrix[i][j]/100 +
                                              Parking_costslist[j]/100) )
                    else:
                        GGRskim[i].append ( int ( totalTime + MultiplyingFactor * Cardistancematrix[i][j] *
                                                kmcharge + Parking_costslist[j]/100) )
            Outputfilename = os.path.join ( Outputdirectory, f'FreeCar_{inc}' )
            Routines.csvwegschrijven ( GGRskim, Outputfilename )

        #Nu FreeTransit
        GGRskim = []
        for i in range (0,number_zones):
            GGRskim.append([])
            for j in range (0,number_zones):
                if TransitTimematrix[i][j]>0.5:
                    GGRskim[i].append(int(TransitTimematrix [i][j]))
                else:
                    GGRskim[i].append(9999)

        Outputfilename = os.path.join(Outputdirectory, 'FreeTransit')
        Routines.csvwegschrijven(GGRskim,Outputfilename)

        #Nu de chains
        #Eerst P+Bike
        if chains :
            for inc in incomes:
                GGRskim = []
                MultiplyingFactor = TVOMwork.get ( inc )
                for i in range (0,number_zones):
                    GGRskim.append([])
                    for j in range (0,number_zones):
                        if Additional_costs:
                            GGRskim[i].append ( int ( PplusBikeTimematrix[i][j] + MultiplyingFactor *
                                                      (PplusBikedistancematrix[i][j] *
                                                      (variablecarcosts + kmcharge) + Additional_costsmatrix[i][j]/100)))
                        else:
                            GGRskim[i].append(int(PplusBikeTimematrix[i][j] + MultiplyingFactor * PplusBikedistancematrix [i][j] *
                                              variablecarcosts+kmcharge))

                Outputfilename = os.path.join(Outputdirectory, f'PplusBike_{Hubname}_{inc}')
                Routines.csvwegschrijven(GGRskim, Outputfilename)

                # Dan P+R

                GGRskim = []

                for i in range ( 0, number_zones ):
                    GGRskim.append ( [] )
                    for j in range ( 0, number_zones ):
                        if Additional_costs:
                            GGRskim[i].append (
                                int ( PplusRDestinationsTimematrix[i][j] + MultiplyingFactor *
                                      (PplusRDestinationsCardistancematrix[i][j] * (variablecarcosts + kmcharge) +
                                         Additional_costsmatrix[i][j] / 100  + KostenDestinationsPplusRTransit[i][j])))
                        else:
                            GGRskim[i].append (
                            int ( PplusRDestinationsTimematrix[i][j] + MultiplyingFactor *
                                  (PplusRDestinationsCardistancematrix[i][j] * (variablecarcosts + kmcharge) +
                                    KostenDestinationsPplusRTransit[i][j] )))

                Outputfilename = os.path.join ( Outputdirectory, f'PplusRDestinations_{Hubname}_{inc}' )
                Routines.csvwegschrijven ( GGRskim, Outputfilename )

                GGRskim = []

                for i in range ( 0, number_zones ):
                    GGRskim.append ( [] )
                    for j in range ( 0, number_zones ):
                        if Additional_costs:
                            GGRskim[i].append (
                                int ( PplusROriginTimematrix + MultiplyingFactor *
                                      (PplusROriginCardistancematrix[i][j] * (variablecarcosts + kmcharge) +
                                         Additional_costsmatrix[i][j] / 100  + KostenOriginPplusRTransit[i][j])))
                        else:
                            GGRskim[i].append (
                            int ( PplusROriginTimematrix[i][j] + MultiplyingFactor *
                                  (PplusROriginCardistancematrix[i][j] * (variablecarcosts + kmcharge) +
                                    KostenOriginPplusRTransit[i][j] )))

                Outputfilename = os.path.join ( Outputdirectory, f'PplusROrigin_{Hubname}_{inc}' )
                Routines.csvwegschrijven ( GGRskim, Outputfilename )
