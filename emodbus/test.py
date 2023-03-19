# copy this back this folder
import emodbus as emb
from pprint import pprint

tcp = emb.ConnTCP('192.168.1.45')
rtu = emb.ConnRTU('COM4')

# {name: (Address:int,functionCode:int,callbackFunction_modbustype:'None|str|tuple|list'),....},
addrs = {
    'Temperature': [1, 4, ('Dec', {'dec': 1})],
    'Humidy': [2, 4, ['Dec', {'dec': 1}]],
    'TemperatureRaw': [1, 4],
    'HumidyRaw': [2, 4],
}
slave = 1
pprint({
    'TCP': tcp.read(addrs, slave),
    'RTU': rtu.read(addrs, slave),
})

# addrs = emb.Addr()
# addrs.add('Temperature', 1, 4, ('Dec', {'dec': 1}))
# tcp.read(addrs, slave),