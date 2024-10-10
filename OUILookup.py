import getopt
import sys
import subprocess
import os
import re
import requests

# Función para obtener los datos de fabricación de una tarjeta de red por IP
# No imprime, simplemente devuelve los resultados
def obtener_datos_por_ip(ip):
    try:
        resultado = subprocess.check_output(["arp", "-a", ip])
        resultado_decodificado = resultado.decode("latin-1")
        fabricante = obtener_fabricante_desde_arp(resultado_decodificado)
        if fabricante:
            return f"IP address: {ip} Fabricante: {fabricante}"
        else:
            return f"IP address: {ip} No se encontró información del fabricante."
    except Exception as e:
        return f"Error: {e}"

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
# No imprime, simplemente devuelve los resultados
def obtener_datos_por_mac(mac):
    try:
        url = f"https://api.maclookup.app/v2/macs/{mac}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['company']:
                return data['company']
            else:
                return "Fabricante no encontrado"
        else:
            return "Error al consultar la API"
    except requests.exceptions.RequestException as e:
        return f"Error de red: {e}"

# Función para procesar la tabla ARP y obtener el fabricante
# No imprime, simplemente devuelve los resultados
def obtener_fabricante_desde_arp(arp_output):
    lines = arp_output.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            mac = parts[1]
            if ip.startswith("192.168.1.") and len(mac) == 17:
                return mac

# Función principal que procesa los argumentos utilizando getopt
# Elimina efectos secundarios y devuelve el resultado
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["mac=", "ip=", "arp", "help"])
    except getopt.GetoptError as err:
        return str(err), None

    mac_address = None
    ip_address = None
    show_arp = False

    for opt, arg in opts:
        if opt == "--mac":
            mac_address = arg
        elif opt == "--ip":
            ip_address = arg
        elif opt == "--arp":
            show_arp = True
        elif opt == "--help":
            return "Use: OUILookup.py --mac <mac> | --ip <ip> | --arp | --help", None

    result = []
    
    if mac_address:
        vendor = obtener_datos_por_mac(mac_address)
        result.append(f"MAC address: {mac_address} \nFabricante: {vendor}")
    elif ip_address:
        resultado = obtener_datos_por_ip(ip_address)
        result.append(resultado)
    elif show_arp:
        response = os.popen("arp -a").read()
        arp_table = re.findall(r"((\d{1,3}\.){3}\d{1,3})\s+(([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})", response)
        result.append("IP/MAC/Vendor:")
        for arp_entry in arp_table:
            ip_address = arp_entry[0]
            mac_address = arp_entry[2]
            if len(mac_address) == 17:
                vendor = obtener_datos_por_mac(mac_address)
                result.append(f"{ip_address} / {mac_address} / {vendor}")
            else:
                result.append(f"{ip_address} / {mac_address} / MAC no válida")
    else:
        result.append("Use: OUILookup.py --mac <mac> | --ip <ip> | --arp | --help")

    return None, result

# Ejecuta la función principal y maneja la salida
if __name__ == "__main__":
    error, output = main()
    if error:
        print(error)
    else:
        for line in output:
            print(line)
