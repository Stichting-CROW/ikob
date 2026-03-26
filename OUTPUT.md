# Output

IKOB produces a directory containing the results of its computation. This document explains the structure.
Note that many of the results are still in dutch.

## Directory structure

for an example of the output see the [reference output of the vlaanderen test](./tests/vlaanderen/reference).
This has the following, fairly typical, structure:

```
reference
├───basis
│   └───werk
│       ├───ervarenreistijd
│       │   └───restdag [f]
│       └───gewichten
│           ├───combinaties
│           │   └───restdag [f]
│           │       ├───elektrisch [f]
│           │       └───fossiel [f]
│           └───restdag [f]
│               ├───elektrisch [f]
│               └───fossiel [f]
├───resultaten
│   └───werk
│       └───alle groepen
│           ├───bestemmingen
│           │   └───restdag [f]
│           ├───inwoners
│           │   └───restdag [f]
│           └───concurrentie
│               ├───bestemmingen
│               │   └───restdag [f]
│               └───inwoners
│                   └───restdag [f]
└───tussenresultaten
    └───groepenverdeling
        └───2023 [f]
```

where [f] indicates that a directory directly contains output files, rather than just other directories.

And now with some explanation:
```
reference
├───basis
│   │ Experienced travel time information
│   │ this combines the monetary and time costs of travel
│   │
│   └───werk
│       │ It's split by motive, as the time value of money is dependent on the travel motive
│       │
│       ├───ervarenreistijd
│       │   │ The actual experienced travel time
│       │   │
│       │   └───restdag [f]
│       │       │ It's split on the time of day, since travel changes throughout the day
│       │       │ Rush hour (spits) vs off peak hours (rest dag) for example
│       │       │ Matches the dagsoort config option and the skims input subdirectory
│       │
│       └───gewichten
│           │ Travel time expressed weights between 0 to 1
│           │ 0 meaning a movement is impossible, 1 meaning it's frictionless
│           │
│           ├───combinaties [f]
│           │   │  Travel weights for when a combination of modalities is available
│           │   │ For each movement, the best modality is chosen
│           │   │
│           │   └───restdag [f]
│           │       │ It's split on the time of day again
│           │       │ Directly contains results for modalities not including car
│           │       │
│           │       ├───elektrisch [f]
│           │       │   │ Results where the modality car is an electric vehicle
│           │       │
│           │       └───fossiel [f]
│           │           │ Results where the modality car is an ICE vehicle
│           │
│           └───restdag [f]
│               │ Travel weights for when when a single modality is available
│               │ Directly contains results for modalities other than car
│               │
│               ├───elektrisch [f]
│               │   │    Results where the modality car is an electric vehicle
│               │
│               └───fossiel [f]
│                   │ Results where the modality car is an ICE vehicle
│
├───resultaten
│   │ Computed results on:
│   │ competition, reachability of destinations and reachability of origins
│   │
│   └───werk
│       │ Split by motive, motive defines the destination and traveling population used
│       │
│       └───alle groepen
│           │ Can contain results on the full population (alle groepen) or only on car owners (alleen autobezitters)
│           │
│           ├───bestemmingen
│           │   │ Reachability of the destination by the traveling population
│           │   │ E.g. The reachability of employers by people aged 18-65
│           │   │
│           │   └───restdag [f]
│           │       │ Split by time of day
│           │
│           ├───inwoners
│           │   │ Reachability of the traveling population by the destinations
│           │   │ E.g. The reachability of people aged 18-65 by employers
│           │   │
│           │   └───restdag [f]
│           │       | Split by time of day
│           │
│           └───concurrentie
│               │ Competition factor to indicate how much a zone has to compete with others
│               │
│               ├───bestemmingen
│               │   │ Competition on destinations by the traveling population
│               │   │ Low if a zone is at a disadvantage compared to other zones in reaching destination
│               │   │ E.g. Low if an employee can only reach jobs that a far away, while those same jobs are nearby for other employees.
│               │   │
│               │   └───restdag [f]
│               │       │ Split by time of day
│               │
│               └───inwoners
│                   │ Competition on the traveling population by destinations
│                   │ Low if there are many destination spots and/or the traveling population is small
│                   │ E.g. Low if employers can only reach employees that a far away, while those same employees are nearby other employers.
│                   │
│                   └───restdag [f]
│                       │ Split by time of day
│
└───tussenresultaten
    | Intermediate results that are stored in the file system, this only contains results on
    |
    └───groepenverdeling
        | The distribution of the population over [groups](./README.md#groups)
        |
        └───2023 [f]
            | Split by urbanization scenario (verstedelijkingsscenario in config)
```

When the ikob code is run for multiple 'time of day' settings, multiple group settings (alle groepen / alleen autobezitters) and multiple [motieven](./README.md#motieven), the results can all be contained in a single output directory with many splits to specify the context of the results. Below is an example output directory with motives 'werk' and 'school', groups 'alle groepen' and 'alleen autobezitters' and times of day 'ochtendspits' and 'restdag'.

```
big_example
├───basis
│   ├───school
│   │   ├───ervarenreistijd
│   │   │   ├───ochtendspits
│   │   │   └───restdag
│   │   └───gewichten
│   │       ├───combinaties
│   │       │   ├───ochtendspits
│   │       │   │   ├───elektrisch
│   │       │   │   └───fossiel
│   │       │   └───restdag
│   │       │       ├───elektrisch
│   │       │       └───fossiel
│   │       ├───ochtendspits
│   │       │   ├───elektrisch
│   │       │   └───fossiel
│   │       └───restdag
│   │           ├───elektrisch
│   │           └───fossiel
│   └───werk
│       ├───ervarenreistijd
│       │   ├───ochtendspits
│       │   └───restdag
│       └───gewichten
│           ├───combinaties
│           │   ├───ochtendspits
│           │   │   ├───elektrisch
│           │   │   └───fossiel
│           │   └───restdag
│           │       ├───elektrisch
│           │       └───fossiel
│           ├───ochtendspits
│           │   ├───elektrisch
│           │   └───fossiel
│           └───restdag
│               ├───elektrisch
│               └───fossiel
├───resultaten
│   ├───school
│   │   ├───alle groepen
│   │   │   ├───bestemmingen
│   │   │   │   ├───ochtendspits
│   │   │   │   └───restdag
│   │   │   ├───concurrentie
│   │   │   │   ├───bestemmingen
│   │   │   │   │   ├───ochtendspits
│   │   │   │   │   └───restdag
│   │   │   │   └───inwoners
│   │   │   │       ├───ochtendspits
│   │   │   │       └───restdag
│   │   │   └───inwoners
│   │   │       ├───ochtendspits
│   │   │       └───restdag
│   │   └───alleen autobezitters
│   │       ├───bestemmingen
│   │       │   ├───ochtendspits
│   │       │   └───restdag
│   │       ├───concurrentie
│   │       │   ├───bestemmingen
│   │       │   │   ├───ochtendspits
│   │       │   │   └───restdag
│   │       │   └───inwoners
│   │       │       ├───ochtendspits
│   │       │       └───restdag
│   │       └───inwoners
│   │           ├───ochtendspits
│   │           └───restdag
│   └───werk
│       ├───alle groepen
│       │   ├───bestemmingen
│       │   │   ├───ochtendspits
│       │   │   └───restdag
│       │   ├───concurrentie
│       │   │   ├───bestemmingen
│       │   │   │   ├───ochtendspits
│       │   │   │   └───restdag
│       │   │   └───inwoners
│       │   │       ├───ochtendspits
│       │   │       └───restdag
│       │   └───inwoners
│       │       ├───ochtendspits
│       │       └───restdag
│       └───alleen autobezitters
│           ├───bestemmingen
│           │   ├───ochtendspits
│           │   └───restdag
│           ├───concurrentie
│           │   ├───bestemmingen
│           │   │   ├───ochtendspits
│           │   │   └───restdag
│           │   └───inwoners
│           │       ├───ochtendspits
│           │       └───restdag
│           └───inwoners
│               ├───ochtendspits
│               └───restdag
└───tussenresultaten
    └───groepenverdeling
        └───2023
```

## File structure

The contents of the various files per path:

### basis/\<motive\>/ervarenreistijd/\<time-of-day\>

The file name indicates the modality and the income class for which the experienced travel time holds.
Remember that this is dependent on the income class because experienced travel time is a combination of time and monetary costs, and different income classes have a different 'time value of money'.

On the modalities in the file name:
- 'no car' / 'GeenAuto' and 'no license' / 'GeenRijbewijs' are added as 'modalities' as they come with their own mode of travel (rental/shared car and taxi respectively) and associated costs.
- Similarly 'free car' and 'free pt' are also 'modalities'.

Each file is a matrix of #zones x #zones indicating the experienced travel time from zone to zone.

The file name and file path then indicate the:
- motive
- time of day
- modality
- income class

to which this travel time applies.

### basis/\<motive\>/gewichten/\<time-of-day\>

File name indicates the modality taken, the preferred modality, and the income class. The split on preferred modality is because a longer travel time is less inhibitive if you have a preference for the modality taken.
Not all taken modalities have all available preferences. For example when the modality is 'free car' the assumption is that the preference can only be car or neutral.

Each file is a matrix of #zones x #zones indicating the travel weight from zone to zone.
0 meaning a movement is impossible, 1 meaning it's frictionless

The file name and file path then indicate the:
- motive
- time of day
- modality
- preferred modality
- income class

to which the weights apply.

The results for ICE and electric vehicles are in subdirectories, but otherwise the same.

### basis/\<motive\>/gewichten/combinaties/\<time-of-day\>

Same results as in [basis/\<motive\>/gewichten/\<time-of-day\>](#basismotivegewichtentime-of-day), with the exception that multiple modalities are described in the file name.

Each file name contains:
- a type of car modality:
  - car
  - free car
  - no car      (so taking a taxi)
  - no license  (so taking a rental car)
  - nothing     (so the car is not considered)
- a type of public transport:
  - public transport
  - free public transport
  - nothing     (so public transport is not considered)
- a type of bike modality:
  - bike
  - nothing     (so cycling is not considered)

And the results contain, for each movement from zone to zone, the highest weight out of all the modalities considered.

Each file is a matrix of #zones x #zones indicating the travel weight from zone to zone. 0 meaning a movement is impossible, 1 meaning it's frictionless

The file name and file path then indicate the:
- motive
- time of day
- combination of modalities
- preferred modality
- income class
to which the weights apply.

The results for ICE and electric vehicles are in subdirectories, but otherwise the the same.


### resultaten/\<motive\>/\<groups\>/bestemmingen/\<time-of-day\>

There are two types of files in this directory. Those starting with "Ontpl_totaal_", and those starting with "Ontpl_totaalproduct_.
All concern how well a destination can be reached by te traveling population.

For all results, the path determines the:
- travel motive
- slice of the population (full population / only car owners)
- time of day

to which the results apply.

#### Ontpl_totaal_

Files containing results on how well the destinations can be reached by the traveling population in each zone.
The file name indicates either the modalities considered or the income class. The file then contains headers to indicate the different income classes or modalities respectively. 

Here all car types (no license / free car / car / etc.) are combined into the modality 'car', and all public transport types are combined into 'pt'.

Each file contains a single array of length #zones indicating how well the traveling population of that zone can reach the destinations of the travel motive.


#### Ontpl_totaalproduct_

This is essentially a preparatory step made so region level aggregation can be made (where the reach of multiple zones in a region are combined). For this you need:

reach_region = (sum_{zones in region} reach_zone x population_size_zone) / population_size_region

Ontpl_totaalproduct contains reach_zone x population_size_zone.

The files contain data of all income classes combined in a single file.
Each file is a matrix of #zones x #income_classes (4).

The modalities to which the results apply can be found in the file name.


### resultaten/\<motive\>/\<groups\>/inwoners/\<time-of-day\>

This directory contains results on how well the traveling population can be reached by the destinations in each zone.

The file structure of this directory is the same as the ['bestemmingen' (destinations) directory](#resultatenmotivegroupsbestemmingentime-of-day), with the exception that destination results filenames are prefixed with 'Ontpl_' (ontplooiing/development), the corresponding 'inwoners' (origins) results are prefixed with 'Pot_' (potentie/potency).

### resultaten/\<motive\>/\<groups\>/concurrentie/bestemmingen/\<time-of-day\>

Same structure as [resultaten/\<motive\>/\<groups\>/bestemmingen/\<time-of-day\>](#resultatenmotiveconcurrentiebestemmingentime-of-day). Ontpl_totaal_ and Ontpl_totaalproduct_ are called Ontpl_conc_ and Ontpl_concproduct_.

Contains results on competition for destinations by the traveling population. A low value indicates that a zone is at a disadvantage compared to other zones in reaching destinations.
Uses the same prefix as [resultaten/\<motive\>/\<groups\>/bestemmingen/\<time-of-day\>](#resultatenmotiveconcurrentiebestemmingentime-of-day) to indicate that this competition is on destination and affects the 'ontplooiing' (development) of citizens.


### resultaten/\<motive\>/\<groups\>/concurrentie/inwoners/\<time-of-day\>

Same structure as [resultaten/\<motive\>/\<groups\>/inwoners/\<time-of-day\>](#resultatenmotivegroupsinwonerstime-of-day). Pot_totaal_ and Pot_totaalproduct_ are called Pot_conc_ and Pot_concproduct_.

Contains results on competition for the traveling population by destinations. A low value indicates that a zone is at a disadvantage compared to other zones in reaching the traveling population.
Uses the same prefix as [resultaten/\<motive\>/\<groups\>/inwoners/\<time-of-day\>](#resultatenmotivegroupsinwonerstime-of-day) to indicate that this competition is on the traveling population and affects the potential reach of a destination.

### tussenresultaten/groepenverdeling/urbanization-scenario

Results on the distribution of the total population over [groups](./README.md#groups).
The file name contains the groups over which to distribute the population (either all groups or only car owners), as well as the motive to which the distribution applies. For example the motive 'work' might distribute the working population over groups while the motive 'school' might distribute the student population over groups. 

Structured as #zones x #groups (60, 15 per income class).

The path indicates to which urbanization scenario (verstedelijkingsscenario in config, matches the SEGS subdirectory) the result apply. The distribution is computed using the general social economic data in the SEGS folder and is based around the urbanization grade of the zones.



