
import pandas as pd


def indices_in(linea, substring):
    posiciones = [linea.rfind(substring)]
    posicion = posiciones[0]
    if posicion != 0 or posicion != -1:
        while True:
            posicion = linea[:posicion].rfind(substring)
            if posicion == 0:
                posiciones.append(0)
                break
            elif posicion == -1:
                break
            else:
                posiciones.append(posicion)
    posiciones.sort()
    return posiciones


def cambiar(pos):
    pos_hex = hex(pos)[2:]
    if len(pos_hex) > 4:
        cambiado = (int(pos_hex[-2:], 16).to_bytes(1, "big") + int(pos_hex[-4:-2], 16).to_bytes(1, "big") +
                    int(pos_hex[:-4], 16).to_bytes(1, "big") + b"\x00")
    else:  # elif len(pos_hex) <= 4:
        cambiado = (int(pos_hex[-2:], 16).to_bytes(1, "big") + int(pos_hex[:-2], 16).to_bytes(1, "big") +
                    b"\x00\x00")
    return cambiado


def cambiar_y_buscar(pos, file):
    if file.count(cambiar(pos)) > 1:
        found = indices_in(file, cambiar(pos))
    else:
        found = file.find(cambiar(pos))
    return found


def abrir(filename):
    with open(f"{filename}.bin", "rb") as a:
        file = a.read()

    if filename == "UnitData":
        inicio_texto = file.rfind(b"\x00\x00\x00") + 3
    else:
        inicio_texto = file.rfind(b"\x00\x00") + 2

    texto = file[inicio_texto:]
    texto = texto.split(b"\x00")[:-1]
    pos = inicio_texto
    final_busc, final_text, final_len = [], [], []

    for i in texto:
        # print(f"Linea: {i}")
        # print(f"tamaño: {len(i)}, byte[pos]: {file[pos].to_bytes(1, 'big')}, int(pos): {pos}, hex(pos): {hex(pos)}")
        final_busc.append(cambiar_y_buscar(pos, file))
        final_text.append(i.decode('utf-8'))
        final_len.append(len(i))
        pos = pos + len(i) + 1

    final = pd.DataFrame({inicio_texto: final_busc, "length": final_len, "text": final_text})
    final.to_csv(f"{filename}.csv", encoding="utf-8", index=False)

    with open(f"{filename}_head.bin", "wb") as head:
        head.write(file[:inicio_texto])

    print(f"Listo. Total líneas: {len(texto)}")


def reemplazar(filename):
    edited_csv = pd.read_csv(f"{filename}.csv", encoding="utf-8")

    with open(f"{filename}_head.bin", "rb") as head:
        head = bytearray(head.read())

    found_on = str(edited_csv.columns[0])
    nuevas_pos = [int(edited_csv.columns[0])]

    for i in range(len(edited_csv['text'])):
        original_length = edited_csv['length'][i]
        if original_length != 0:
            if edited_csv['text'][i].count("♪") > 0:
                edited_length = len([letra for letra in edited_csv['text'][i] if letra != "♪"]) + edited_csv['text'][
                    i].count("♪") * 3
            else:
                edited_length = len(edited_csv['text'][i])

            head = head + (edited_csv['text'][i]).encode() + b"\x00"
            by = nuevas_pos[-1] + edited_length + 1

            try:
                try:
                    camb = int(edited_csv[found_on][i + 1])
                    for h in range(len(cambiar(by))):
                        head[camb + h] = cambiar(by)[h]
                except ValueError:
                    camb = [int(e) for e in edited_csv[f"{edited_csv.columns[0]}"][i + 1].strip('][').split(', ')]
                    for k in camb:
                        for h in range(len(cambiar(by))):
                            head[k + h] = cambiar(by)[h]
            except KeyError:
                pass

            nuevas_pos.append(by)

        elif original_length == 0:
            head = head + b"\x00"
            by = nuevas_pos[-1] + 1
            nuevas_pos.append(by)

    with open(f"{filename}_final.bin", "wb") as final:
        final.write(head)

    print(f"Listo.")


def main():
    filenames = ["UnitData", "DictionaryData", "FevData"]

    while True:
        sel = int(input("1: Extraer texto/2: Inyectar texto: "))
        if sel == 1:
            for filename in filenames:
                print(f"Extrayendo texto de {filename}...", end=" ")
                abrir(filename)
            break
        elif sel == 2:
            for filename in filenames:
                print(f"Inyectando texto de {filename}...", end=" ")
                reemplazar(filename)
            break
        else:
            print("Selección no válida, selecciona nuevamente.")
    input("Presiona Enter para finalizar...")
  

main()
