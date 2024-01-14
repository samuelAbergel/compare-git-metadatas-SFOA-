import os
import pandas as pd

def list_metadata_names(folder_path, excluded_types, file_extensions, metadata_dict):
    metadata_names = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Retirer '-meta.xml' si présent
            # Client_Record_Page.flexipage-meta.xml
            # row-app/main/default/flexipages/Client_Record_Page.flexipage-meta.xml
            # row-app /main/default/  Client_Record_Page.flexipage-meta.xml
            full_path = os.path.join(root, file)
            # print('full_path : ' + full_path)
            folder = 'COMMON' if folder_path == common_path else 'SFOA' if folder_path == sfoa_path else 'ROW'
            if file.endswith('-meta.xml'):
                file = file[:-9]  # Supprimer '-meta.xml'
                file_extension = os.path.splitext(file)[1]
                file_name = os.path.basename(file)[:- len(file_extension)]
                metadata_type = file_extension[1:]
                #print('full_path : ' + full_path + ' file_extension : ' + file_extension + ' file_name : ' + file_name + ' metadata_type : ' + metadata_type)
                key = (root[len(folder_path) + 1:] + file_name)
                if file_extension in file_extensions or file_extension not in excluded_types:
                    if key not in metadata_dict:
                        metadata_dict[key] = {
                                    'File Name': file_name,
                                    'File Type': metadata_type,
                                    'Full Path Row': full_path if folder_path == row_path else None,
                                    'Full Path Sfoa': full_path if folder_path == sfoa_path else None,
                                    'Full Path Force': full_path if folder_path == common_path else None,
                                    'Found In' : folder,
                                    'is Identical' : 'N/A'
                                    }
                    else:
                        if folder_path == row_path:
                            metadata_dict[key]['Full Path Row'] = full_path
                        if folder_path == sfoa_path:
                            metadata_dict[key]['Full Path Sfoa'] = full_path
                        if folder_path == common_path:
                            metadata_dict[key]['Full Path Force'] = full_path
                        metadata_dict[key]['Found In'] += (','+ folder)
                        metadata_dict[key]['is Identical'] = compare_metadata_content(metadata_dict[key]['Full Path Row'], metadata_dict[key]['Full Path Sfoa'], metadata_dict[key]['Full Path Force'])

    return metadata_dict

def read_metadata_content(file_path):
    if file_path is not None and os.path.exists(file_path):
        # pour les classes et triggers il faut comparer les cls et et pas les cls-meta.xml
        path_to_open = file_path[:-9] if os.path.exists(file_path[:-9]) else file_path

        try:
            with open(path_to_open, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            return None
    return None

def compare_metadata_content(full_path_row, full_path_sfoa, full_path_force):
    file_paths = [full_path_row, full_path_sfoa, full_path_force]
    contents = [read_metadata_content(path) for path in file_paths]
    # Filtrer les contenus None et comparer
    contents = [content for content in contents if content is not None]
    return len(set(contents)) == 1 if contents else False


# Demander à l'utilisateur de saisir les chemins relatifs
common_path = input("Veuillez saisir le chemin relatif pour COMMON : ")
sfoa_path = input("Veuillez saisir le chemin relatif pour SFOA : ")
row_path = input("Veuillez saisir le chemin relatif pour ROW : ")

folders = [common_path, sfoa_path, row_path]
excluded_types = ('.email', '.emailFolder', '.report', '.reportType', '.dashboard', '.dashboardFolder', '.ico', '.reportFolder', '.crt', '', '.mno', '.log', '.bin', '.dmp', '.design', '.evt', '.indx', '.eot', '.json', '.config', '.design', '.zip', '.ttf', '.jpeg', '.resource', '.woff', '.html',  '.js', '.css', '.txt', '.svg', '.png', '.gif', '.jpg', '.map', '.auradoc')
file_extensions = ['.cls', '-meta.xml', '.object', '.page', '.cmp', '.flexipage', '.globalValueSetTranslation', '.letter', '.community', '.queue', '.autoResponseRules', '.escalationRules', '.homePageLayout', '.corsWhitelistOrigin', '.namedCredential',  '.notifications', '.role',  '.documentFolder', '.connectedApp', '.homePageComponent', '.iframeWhiteListUrlSettings',  '.group', '.remoteSite', '.profile', '.weblink', '.testSuite', '.asset', '.profileSessionSetting', '.labels', '.deployment', '.permissionsetgroup', '.LeadConvertSetting', '.globalValueSet',   '.quickAction', '.cleanDataService',  '.standardValueSet', '.matchingRule', '.duplicateRule', '.assignmentRules', '.app',  '.component', '.trigger', '.layout', '.fieldTranslation', '.objectTranslation', '.document', '.topicsForObjects', '.field', '.webLink', '.md', '.workflow', '.sharingRules', '.settings', '.permissionset', '.profilePasswordPolicy', '.listView', '.tab', '.translation', '.validationRule', '.recordType', '.businessProcess', '.standardValueSetTranslation', '.paymentGatewayProvider', '.compactLayout', '.samlssoconfig', '.flow', '.installedPackage', '.flowDefinition']


metadata_dict = {}
for folder in folders:
    list_metadata_names(folder, excluded_types, file_extensions, metadata_dict)

# Conversion du dictionnaire en DataFrame
metadata_df = pd.DataFrame.from_dict(metadata_dict, orient='index')

# Sélection des colonnes pertinentes
# Assurez-vous que les noms des colonnes correspondent exactement aux clés du dictionnaire
metadata_df = metadata_df[['File Name', 'File Type', 'Found In', 'is Identical']]

# Écriture du DataFrame dans un fichier Excel
try:
    with pd.ExcelWriter('MetadataSummary.xlsx') as writer:
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
except Exception as e:
    print(f"Erreur lors de l'écriture dans le fichier Excel: {e}")
