import pandas as pd
import glob

def get_schoolName(code, keyDict): 
    try: 
        return keyDict[code] 
    except KeyError: 
        return code 

CountyDF = pd.read_csv('data_files/sb_ca15-24_all.csv')
CountyDF = CountyDF[CountyDF['County Code'].isin([0, 44])] # 0 is State, 44 is Santa Cruz

groupsKey = pd.read_csv('data_files/StudentGroups_2023.txt',  encoding="ISO-8859-1", delimiter='^').set_index('Demographic ID Num')

# Concat all entities files
entities_files = glob.glob('data_files/*entities_csv.txt')
entities = pd.concat([pd.read_csv(f, encoding="ISO-8859-1",  delimiter='^') for f in entities_files])
entities = entities.drop_duplicates(subset=['District Code', 'School Code'])
entities = pd.read_csv('data_files/sb_ca2024entities_csv.txt', encoding="ISO-8859-1",  delimiter='^')

districts = entities[['District Code', 'District Name', 'School Code']]
districtsKey = districts[['District Code', 'District Name']][districts["School Code"]== 0000000].set_index('District Code').to_dict()['District Name']

schools = entities[['School Code', 'School Name']]
schoolsKey = schools.set_index('School Code').to_dict()['School Name']
schoolsKey[100305] = 'Cypress Charter High'
schoolsKey[123083] = 'Home and Hospital'
schoolsKey[4475432] = 'District Level Program'

# Associate Cypress Charter High (100305) to SC COE district
CountyDF['District Code'][CountyDF['School Code'] == 100305] = 10447  
CountyDF['District Code'][(CountyDF['District Code'] == 69765) & (CountyDF['Grade'] == 11)] = 10447 # All LO Grade 11 data is from Cypress High

CountyDF['Student Groups'] = CountyDF['Subgroup ID'].map(lambda x: groupsKey['Demographic Name'].to_dict()[x])
CountyDF['Student Group Category'] = CountyDF['Subgroup ID'].map(lambda x: groupsKey['Student Group'].to_dict()[x])
CountyDF['District'] = CountyDF['District Code'].map(lambda x: districtsKey[x] if x in districtsKey else x)
CountyDF['School'] = CountyDF['School Code'].apply(lambda x: get_schoolName(x, schoolsKey))

CountyDF.to_csv('CAASPP_STATE.csv', index=False)
