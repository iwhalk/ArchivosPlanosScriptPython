import os
import sys
import pandas as pd

files = []
path_files = ""
list_diff_ocu = []
list_folios_duplic = []
list_folios_duplic_single = []

resultado = []
count_two = 0


def more_events(val, file_nine, lane_dupli=False):
    global count_two
    if lane_dupli:
        count_occurrences = 0
        for i, r in val.iterrows():
            count_occurrences += (r.e - r.d) + 1

        count_two += count_occurrences
        occurrences_found = int(open(path_files + file_nine, 'r').read()
                                .count(val.head(1).iloc[0]['combined']))

        difference = occurrences_found - count_occurrences

        if difference != 0 and val.head(1).iloc[0]['combined'] + ": " + str(difference) not in list_diff_ocu:
            list_diff_ocu.append(val.head(1).iloc[0]['combined'] + ": "
                                 + str(difference))
    else:
        count_occurrences = (val.iloc[0]['e'].astype(int) -
                             val.iloc[0]['d'].astype(int)) + 1

        count_two += count_occurrences

        occurrences_found = int(open(path_files + file_nine, 'r').read()
                                .count(val.iloc[0]['combined']))

        difference = occurrences_found - count_occurrences

        if difference != 0 and val.iloc[0]['combined'] + ": " + str(difference) not in list_diff_ocu:
            list_diff_ocu.append(val.iloc[0]['combined'] + ": "
                                 + str(difference))


def open_files():
    global path_files

    path_files = 'C:\\ArchivosPlanosWeb\\'
    list_files = [f for f in os.listdir(path_files)]

    if len(list_files) < 2:
        raise ValueError(
            'No se encontraron Archivos 2A ni 9A en esta carpeta')

    global files
    files = list(filter(lambda x: x.endswith("2A")
                        or x.endswith("9A"), list_files))

def eventos_nuevos(df_occur_dosA, file_nine):
    nineA_data = pd.read_csv(path_files + '/' + file_nine, decimal=",", skiprows=1,encoding='utf8',
                          usecols=(3, 4, 5), names=["a", "b", "c"])

    df_nueveA = pd.DataFrame(nineA_data)
    df_nueveA["combined"] = df_nueveA["a"].astype(int).astype(str) + "," \
        + df_nueveA["b"].astype(int).astype(str) + "," + df_nueveA["c"]
    df_nueveA = df_nueveA['combined'].drop_duplicates()

    p = df_nueveA.isin(df_occur_dosA)
    indexes = p[p].index.values
    df_nueveA.drop(index=indexes, inplace=True)
    if(len(df_nueveA)):
        list_folios_duplic_single.append(df_nueveA.values.tolist())


def calculate(file_two, file_nine):
    my_data = pd.read_csv(path_files + file_two, decimal=",", skiprows=1,encoding='utf8',
                          usecols=(4, 5, 6, 8, 9), names=["a", "b", "c", "d", "e"])

    df = pd.DataFrame(my_data)

    df = df.reset_index()
    df["Linea"] = "Linea " + (df["index"].astype(int) + 2).astype(str)

    indexs = df[(df['d'].astype(int) == 0) & (df['e'].astype(int) == 0)].index

    df.drop(index=indexs, inplace=True)

    df["combined"] = df["a"].astype(int).astype(str) + "," \
        + df["b"].astype(int).astype(str) + "," + df["c"]

    df_dosA = df["combined"].drop_duplicates()

    df_occur = pd.DataFrame()
    df_occur['freq'] = df['combined'].value_counts()
    eventos_nuevos(df_dosA, file_nine)

    #list_folios_duplic = None
    # Para carriles que no tienen mas de dos folios de inicio en el archivo
    for i, row in df_occur.iterrows():
        val = df[df['combined'] == row.name]
        
        #more_events(val, file_nine)
        vals = []
        for d, e in zip(val.d, val.e):
            vals.append(e)
            vals.append(d)

        df1 = pd.DataFrame({'combined': vals})

        df_occur1 = pd.DataFrame()
        df_occur1['freq'] = df1['combined'].value_counts()

        folio_duplic = df_occur1[df_occur1['freq'] > 1].index.tolist()

        # PENDIENTE: PREGUNTAMOS SI HAY OCURR MAYOR A 2, SI ES VERDAD ENTONCES MANDAMOS A LISTA DE DE FOLIOS
        # SI NO, RECORREMOS UNA POR UNA LAS FILAS DE VAL Y SI NO, SUMAMOS Y BUSCAMOS
        if row.freq < 2 and len(folio_duplic) < 1:
            more_events(val, file_nine)
        else:
            if len (folio_duplic):
                for v in folio_duplic:
                    
                    df2 = val[(val['d'].astype(int) == v) | (val['e'].astype(int) == v)]

                    if len(df2) == 1:
                        more_events(val, file_nine, True)
                    elif len(df2) > 1:
                        if(df2[['combined', 'd', 'e']].values.tolist() not in list_folios_duplic):
                            list_folios_duplic.append(df2[['combined', 'd', 'e', 'Linea']].values.tolist())
                    else:
                        more_events(val, file_nine, True)
            else:
                more_events(val, file_nine, True)

    list_diffe = []
    if len(list_folios_duplic):
        #resultado.append("Turno " + file_two[-3] + " con folios duplicados")
        tmp = []
        tmp.append("Turno " + file_two[-3] + " con folios duplicados")
        list_diffe += tmp
        list_diffe += list_folios_duplic
        tmp.clear()

    if len(list_folios_duplic_single):
        # Sacamos diferencia
        header_nine = ''
        with open(path_files + file_nine, 'r') as f:
            header_nine = f.readline()
        tmp = []

        tmp.append("Turno " + file_two[-3] + ": " + \
            str(int(header_nine[-6:]) - count_two) + " Los siguientes folios no estan en el archivo 2A: ")      
        
        list_diffe += tmp
        list_diffe += list_folios_duplic_single
        tmp.clear()

    if len(list_diff_ocu):
        # Sacamos diferencia
        header_nine = ''
        with open(path_files + file_nine, 'r') as f:
            header_nine = f.readline()

        #resultado.append("Turno " + file_two[-3] + ": " + \
        #    str(int(header_nine[-6:]) - count_two))

        tmp = []
        tmp.append("Turno " + file_two[-3] + ": " + \
            str(int(header_nine[-6:]) - count_two))
        list_diffe += tmp
        list_diffe += list_diff_ocu
        tmp.clear()

    if len(list_folios_duplic) == 0 and len(list_diff_ocu) == 0 and len(list_folios_duplic_single) == 0:
        header_nine = ''
        with open(path_files + file_nine, 'r') as f:
            header_nine = f.readline()
        
        conteo9A = int(header_nine[-6:]) - count_two

        if(conteo9A == 0):
            result = "Turno " + file_two[-3] + ": " + \
                str(int(header_nine[-6:]) - count_two) + " Todo bien"
        else:
            result = "Turno " + file_two[-3] + ": " + \
                str(int(header_nine[-6:]) - count_two) + " Sugerencia: Revisa el encabezado de archivo 9A"

        return result, list_diff_ocu
    else:
        return resultado, list_diffe


if __name__ == '__main__':
    try:
        open_files()
        if len(files):
            files_4 = list(filter(lambda x: x.endswith('42A')
                                  or x.endswith('49A'), files))

            files_5 = list(filter(lambda x: x.endswith('52A')
                                  or x.endswith('59A'), files))

            files_6 = list(filter(lambda x: x.endswith('62A')
                                  or x.endswith('69A'), files))

            if len(files_4):
                result, list_diff = calculate(next((f for f in files_4 if f.endswith('2A')), None),
                                              next((f for f in files_4 if f.endswith('9A')), None))

                if len(result) != 0:
                    print(result)
                    for p in list_diff:
                        print(f"\t{p}", end="\n")
                else:
                    for p in list_diff:
                        print(f"\t{p}", end="\n")

                list_diff_ocu = []
                list_folios_duplic = []
                list_folios_duplic_single = []
                list_diffe = []
                resultado = []
                count_two = 0

            if len(files_5):
                result, list_diff = calculate(next((f for f in files_5 if f.endswith('2A')), None),
                                              next((f for f in files_5 if f.endswith('9A')), None))
                if len(result) != 0:
                    print(result)
                    for p in list_diff:
                        print(f"\t{p}", end="\n")
                else:
                    for p in list_diff:
                        print(f"\t{p}", end="\n")

                list_diff_ocu = []
                list_folios_duplic = []
                list_folios_duplic_single = []
                list_diffe = []
                resultado = []
                count_two = 0

            if len(files_6):
                result, list_diff = calculate(next((f for f in files_6 if f.endswith('2A')), None),
                                              next((f for f in files_6 if f.endswith('9A')), None))
                if len(result) != 0:
                    print(result)
                    for p in list_diff:
                        print(f"\t{p}", end="\n")
                else:
                    for p in list_diff:
                        print(f"\t{p}", end="\n")

                list_diff_ocu = []
                list_folios_duplic = []
                list_folios_duplic_single = []
                list_diffe = []
                resultado = []
                count_two = 0
        else: 
            print("No se encontraron Archivos 2A ni 9A en esta carpeta\n")

    except BaseException:
        import sys
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())

