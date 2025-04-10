import pandas as pd
import numpy
import os
import argparse

def limit(group_df, metric):
    # Caclular mediana
    median = numpy.median(group_df[metric])
    
    # Calcular desvio padrão(
    desv = numpy.std(group_df[metric])

    # Definir faixa
    low = median - desv
    high = median + desv

    return low, high

def main(camera_dir):
    # Abrir arquivo
    excel_file_path = os.path.join(camera_dir, "comparacao.xlsx")
    comparison_table = pd.read_excel(excel_file_path)

    # Adicionar coluna "boa"
    comparison_table["Foto Boa"] = [0]*len(comparison_table)

    # Criar lista com os grupos
    groups = list(set(comparison_table["Grupo"].tolist()))
    metrics = ["Desfoque", "Contraste", "Ruído"]

    first_good_photos = []

    for group in groups:
        count = 0

        # Acessar a parte da tabela de cada grupo
        group_df = comparison_table.loc[comparison_table["Grupo"] == group]

        # Verificar cada linha do group_df
        for index, row in comparison_table.loc[comparison_table["Grupo"] == group].iterrows():
            good_photo = True

            # Verificar cada métrica da linha
            for metric in metrics:
                low, high = limit(group_df, metric)
                value = row[metric]

                if value < low or value > high:
                    good_photo = False
                    break

            if good_photo:

                # Salvar primeira imagem na lista good_images
                count+= 1
                if count == 1:
                    first_good_photos.append(comparison_table.loc[index, "Imagem"])
                
                # Alterar status de foto boa
                comparison_table.loc[index, "Foto Boa"] = 1

    # RELATÓRIO

    relatorio_path = os.path.join(camera_dir,"relatorio.txt")
    file = open(relatorio_path, "w")

    # Achar a moda das primeiras boas imagens e quantas vezes aquela imagem foi a primeira
    values, count = numpy.unique(first_good_photos, return_counts=True)
    mode_index = numpy.argmax(count)
    moda = values[mode_index]
    first_good_photos_rate = count[mode_index]/len(first_good_photos)

    file.write(f"Primeira boa imagem em {first_good_photos_rate*100}% dos grupos: {moda}\n")

    # Calcular taxa de boas fotos no geral
    good_photos_number = comparison_table["Foto Boa"].value_counts()[1]
    good_photos_rate = good_photos_number/len(comparison_table)

    file.write(f"Taxa de boas fotos: {good_photos_rate*100}%")

    file.close()

    # Salva a tabela atualizada em um novo arquivo excel
    with pd.ExcelWriter(excel_file_path) as writer:
        comparison_table.to_excel(writer, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--diretorio", type=str, required=True, help="Diretório da câmera, onde se encontra a tabela comparativa"
    )

    args = parser.parse_args()
    main(args.diretorio)