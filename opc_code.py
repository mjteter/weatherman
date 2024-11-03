# from typing import Dict, List
import requests
import socket
import asyncio
import logging
import psychro.lib as psy
# from pathlib import Path
from datetime import datetime, timedelta

# from cryptography import x509
# from cryptography.hazmat.primitives.serialization import Encoding
# from cryptography.x509.oid import ExtendedKeyUsageOID
# from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from asyncua import Server  # , ua
# from asyncua.crypto.uacrypto import load_certificate, load_private_key
# from asyncua.crypto.cert_gen import (generate_private_key, generate_self_signed_app_certificate,
#                                      dump_private_key_as_pem, generate_app_certificate_signing_request,
#                                      sign_certificate_request)


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
# logger levels: NOTSET   =  0
#                DEBUG    = 10
#                INFO     = 20
#                WARN     = 30
#                ERROR    = 40
#                CRITICAL = 50


# HOSTNAME: str = socket.gethostname()
#
# # used for subject common part
# NAMES: Dict[str, str] = {
#     'countryName': 'US',
#     'stateOrProvinceName': 'PA',
#     'localityName': 'Philadelphia',
#     'organizationName': 'University of Pennsylvania FRES'
# }
#
# CLIENT_SERVER_USE = [ExtendedKeyUsageOID.CLIENT_AUTH, ExtendedKeyUsageOID.SERVER_AUTH]
#
# # setup the paths for the cerst, keys and csr
# base = Path('certificates')
# base_csr: Path = base / 'csr'
# base_private: Path = base / 'private'
# base_certs: Path = base / 'certs'
# base_csr.mkdir(parents=True, exist_ok=True)
# base_private.mkdir(parents=True, exist_ok=True)
# base_certs.mkdir(parents=True, exist_ok=True)
#
#
# def generate_private_key_for_myserver():
#     key: RSAPrivateKey = generate_private_key()
#     key_file = base_private / 'myserver.pem'
#     key_file.write_bytes(dump_private_key_as_pem(key))
#
#
# async def generate_self_signed_certificate():
#     subject_alt_names: List[x509.GeneralName] = [x509.UniformResourceIdentifier(
#         f'urn:{HOSTNAME}:foobar:myselfsignedServer'), x509.DNSName(f'{HOSTNAME}')]
#
#     # key: RSAPrivateKey = generate_private_key()
#     key = await load_private_key(base_private / 'myserver.pem')
#
#     cert: x509.Certificate = generate_self_signed_app_certificate(key, f'myselfsignedserver@{HOSTNAME}',
#                                                                   NAMES, subject_alt_names, extended=CLIENT_SERVER_USE)
#
#     cert_file = base_certs / 'myserver-selfsigned.der'
#     cert_file.write_bytes(cert.public_bytes(encoding=Encoding.DER))
#
#
# def generate_applicationgroup_ca():
#     subject_alt_names: List[x509.GeneralName] = [x509.UniformResourceIdentifier(f'urn:{HOSTNAME}:foobar:myserver'),
#                                                  x509.DNSName(f'{HOSTNAME}')]
#
#     key: RSAPrivateKey = generate_private_key()
#     cert: x509.Certificate = generate_self_signed_app_certificate(key, 'Application CA', NAMES,
#                                                                   subject_alt_names, extended=[])
#
#     key_file = base_private / 'ca_application.pem'
#     cert_file = base_certs / 'ca_application.der'
#
#     key_file.write_bytes(dump_private_key_as_pem(key))
#     cert_file.write_bytes(cert.public_bytes(encoding=Encoding.DER))
#
#
# async def generate_csr():
#     subject_alt_names: List[x509.GeneralName] = [x509.UniformResourceIdentifier(f'urnn:{HOSTNAME}:foobar:myserver'),
#                                                  x509.DNSName(f'{HOSTNAME}')]
#
#     key: RSAPrivateKey = generate_private_key()
#     key = await load_private_key(base_private / 'myserver.pem')
#     csr: x509.CertificateSigningRequest = generate_app_certificate_signing_request(key,
#                                                                                    f'myserver{HOSTNAME}',
#                                                                                    NAMES, subject_alt_names,
#                                                                                    extended=CLIENT_SERVER_USE)
#
#     # key_file = base_private / 'myserver.pem'
#     csr_file = base_csr / 'myserver.csr'
#
#     # key_file.write_bytes(dump_private_key_as_pem(key))
#     csr_file.write_bytes(csr.public_bytes(encoding=Encoding.PEM))
#
#
# async def sign_csr():
#     issuer = await load_certificate(base_certs / 'ca_application.der')
#     key_ca = await load_private_key(base_private / 'ca_application.pem')
#     csr_file: Path = base_csr / 'myserver.csr'
#     csr = x509.load_pem_x509_csr(csr_file.read_bytes())
#
#     cert: x509.Certificate = sign_certificate_request(csr, issuer, key_ca, days=30)
#     (base_certs / 'myserver.der').write_bytes(cert.public_bytes(encoding=Encoding.DER))


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def get_upenn_grid(api_header):
    response = {'properties': {'gridId': 'PHI', 'gridX': 49, 'gridY': 76}}
    try:
        response = requests.get('https://api.weather.gov/points/39.9509,-75.1941', headers=api_header).json()
    except TimeoutError:  # , ConnectTimeoutError:
        _logger.error('No response to grid request.  Grid set to default of (49,76)')
    finally:
        resp_grids = (response['properties']['gridId'] + '/' + str(response['properties']['gridX']) + ',' +
                      str(response['properties']['gridY']))

    return resp_grids


async def get_upenn_forecast(api_header, api_grids, server, pt_map_dict):
    api_url = 'https://api.weather.gov/gridpoints/' + api_grids + '/forecast/hourly'

    # keep trying to get connection until dns provides good ip
    good_connection = False
    while not good_connection:
        api_ip = socket.gethostbyname('api.weather.gov')

        try:
            _logger.info('Attempt to make connection to api.weather.gov.')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('api.weather.gov', 443))
        except OSError:
            _logger.error(f'No response from api.weather.gov at {api_ip}, wait 30 seconds and try again.')
            await asyncio.sleep(30)
        else:
            _logger.info(f'Successful connection made with api.weather.gov at {api_ip}.')
            s.close()
            good_connection = True

    try:
        response = requests.get(api_url, headers=api_header).json()
    except TimeoutError:  # , ConnectTimeoutError:
        response = None

    await handle_forecast_data(response, server, pt_map_dict)

    return response


async def handle_forecast_data(response, server, pt_map_dict):
    if response is None:
        return

    wthr_gov_time_frmt = '%Y-%m-%dT%H:%M:%S%z'
    opc_srvr_time_frmt = '%Y-%m-%d %H:%M:%S'

    _logger.info('Update OPC server with latest data.')

    await server.get_node(pt_map_dict['_generatedAt']).write_value(datetime.strptime(
        response['properties']['generatedAt'], wthr_gov_time_frmt).astimezone(None).strftime(opc_srvr_time_frmt))
    await server.get_node(pt_map_dict['_updateTime']).write_value(datetime.strptime(
        response['properties']['updateTime'], wthr_gov_time_frmt).astimezone(None).strftime(opc_srvr_time_frmt))

    for period in response['properties']['periods']:
        # if period['number'] > 10:
        #     continue
        hr_name = 'hour' + str(period['number'] - 1).zfill(3)

        # calculate some psychrometric values
        db = float(period['temperature'])
        rh = float(period['relativeHumidity']['value'])
        calcdp = psy.dewPoint(psy.Temperature(db, 'F'), rh)
        calcdp.toF()
        calchr = psy.humidityRatio(psy.Temperature(db, 'F'), rh, psy.Pressure(1.0, 'atm'))[0] * 7000.0
        try:
            wndspd = float(period['windSpeed'][:-4])
        except ValueError:
            wndspd = 0.0

        # update opc server
        await server.get_node(pt_map_dict[hr_name]['startTime']).write_value(
            datetime.strptime(period['startTime'], wthr_gov_time_frmt).astimezone(None).strftime(opc_srvr_time_frmt))
        await server.get_node(pt_map_dict[hr_name]['temperature']).write_value(float(db))
        await server.get_node(pt_map_dict[hr_name]['relativeHumidity']).write_value(float(rh))
        await server.get_node(pt_map_dict[hr_name]['calcDewPoint']).write_value(float(calcdp.getValue()))
        await server.get_node(pt_map_dict[hr_name]['calcHumidityRatio']).write_value(float(calchr))
        await server.get_node(pt_map_dict[hr_name]['windSpeed']).write_value(wndspd)
        await server.get_node(pt_map_dict[hr_name]['windDirection']).write_value(period['windDirection'])
        await server.get_node(pt_map_dict[hr_name]['shortForecast']).write_value(period['shortForecast'])
        await server.get_node(pt_map_dict[hr_name]['probabilityOfPrecipitation']).write_value(
            float(period['probabilityOfPrecipitation']['value']))

        # print('NEW', await server.get_node(pt_map_dict[hr_name]['startTime']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['temperature']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['relativeHumidity']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['calcDewPoint']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['calcHumidityRatio']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['windSpeed']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['windDirection']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['shortForecast']).get_value())
        # print('NEW', await server.get_node(pt_map_dict[hr_name]['probabilityOfPrecipitation']).get_value())

    _logger.info('OPC server updated.')
    return


async def gen_opc_point_map(server, ns):
    wthr = await server.nodes.objects.add_folder(ns, 'Weather')
    frcst = await wthr.add_folder(ns, 'Forecast')

    dt_frmt = '%Y-%m-%d %H:%M:%S'
    default_dt = datetime.strptime('2024-01-01 00:00:00', dt_frmt)

    genat = await frcst.add_variable(ns, '_generatedAt', default_dt.strftime(dt_frmt))
    updttm = await frcst.add_variable(ns, '_updateTime', default_dt.strftime(dt_frmt))

    pt_map_dict = {'_generatedAt': genat.nodeid, '_updateTime': updttm.nodeid}

    for hr in range(156):  # 156 is the standard set of hours provided from api
        hr_name = 'hour' + str(hr).zfill(3)  # set name of objects to format 'hourXXX'
        hr_obj = await frcst.add_object(ns, hr_name)  # make opc object
        pt_map_dict[hr_name] = {'self': hr_obj.nodeid}  # add to dict for easy access

        # add all relevant points as children to hr_obj
        hr_strt = default_dt + timedelta(hours=hr)

        strttm = await hr_obj.add_variable(ns, 'startTime', hr_strt.strftime(dt_frmt))
        temp = await hr_obj.add_variable(ns, 'temperature', 50.0)
        relhum = await hr_obj.add_variable(ns, 'relativeHumidity', 50.0)
        clcdp = await hr_obj.add_variable(ns, 'calcDewPoint', 32.1)
        clchr = await hr_obj.add_variable(ns, 'calcHumidityRatio', 26.0)
        wndspd = await hr_obj.add_variable(ns, 'windSpeed', 0.0)
        wnddir = await hr_obj.add_variable(ns, 'windDirection', '')
        shtfrct = await hr_obj.add_variable(ns, 'shortForecast', '')
        prbprcp = await hr_obj.add_variable(ns, 'probabilityOfPrecipitation', 0.0)

        # add points to dict
        pt_map_dict[hr_name]['startTime'] = strttm.nodeid
        pt_map_dict[hr_name]['temperature'] = temp.nodeid
        pt_map_dict[hr_name]['relativeHumidity'] = relhum.nodeid
        pt_map_dict[hr_name]['calcDewPoint'] = clcdp.nodeid
        pt_map_dict[hr_name]['calcHumidityRatio'] = clchr.nodeid
        pt_map_dict[hr_name]['windSpeed'] = wndspd.nodeid
        pt_map_dict[hr_name]['windDirection'] = wnddir.nodeid
        pt_map_dict[hr_name]['shortForecast'] = shtfrct.nodeid
        pt_map_dict[hr_name]['probabilityOfPrecipitation'] = prbprcp.nodeid

    # pprint.pprint(pt_map_dict, compact=True)

    # await server.get_node(pt_map_dict['hour000']['temperature']).write_value(70.0)
    # print(await server.get_node(pt_map_dict['hour000']['temperature']).get_value())
    return pt_map_dict


async def main(url, ns, api_header, api_grids):
    # # create key and reuse it for self_signed and generate_csr
    # generate_private_key_for_myserver()
    #
    # # generate self signed certificate for myserver-selfsigned
    # await generate_self_signed_certificate()
    #
    # # generate certificate signing request and sign it with the ca for myserver
    # generate_applicationgroup_ca()
    # await generate_csr()
    # await sign_csr()
    #
    # return

    # initialize opc ua server
    server = Server()
    await server.init()
    server.set_endpoint(url)

    # set up namespace
    idx = await server.register_namespace(ns)

    pt_map_dict = await gen_opc_point_map(server, idx)

    _logger.info('Starting server!')
    async with server:
        try:
            # await get_upenn_forecast(api_header, api_grids, server, pt_map_dict)
            while True:
                await get_upenn_forecast(api_header, api_grids, server, pt_map_dict)
                await asyncio.sleep(300)
        except KeyboardInterrupt:
            pass

            # await asyncio.sleep(1)
            # new_val = await myvar.get_value() + 0.1
            # _logger.info('Set value of %s to %.1f', myvar, new_val)
            # await myvar.write_value(new_val)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    socket.setdefaulttimeout(3)

    header = {'User-Agent': '(UofP FRES, fresscada@pobox.upenn.edu)', 'accept': 'application/geo+json'}
    grids = get_upenn_grid(header)

    # get local ip and computer name
    local_ip = get_ip()
    # local_name = socket.gethostname()

    opc_url = 'opc.tcp://' + local_ip + ':49320/pennpyopc/server/'
    # opc_ns = 'urn:' + local_name + ':upenn.weatherforecast:UAServer'  # 'http://examples.freeopcua.github.io'
    opc_ns = 'PennPyWeatherServer'

    asyncio.run(main(opc_url, opc_ns, header, grids), debug=False)