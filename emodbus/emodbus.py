from abc import ABC, abstractmethod
import serial
import serial.tools.list_ports as ls
import minimalmodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Defaults
from . import modbustypes as mbt


def getSerials(all: bool = False) -> list[dict]:
    """Get all or only ative (all=False) Serials of the computer

    Args:
        all (bool, optional): If True collect all Serials, if False collect only with PID. Defaults to False.

    Returns:
        list[dict]: List of Serials. Each item has a dictionary with data of serial (name, device, description, hwid, location, manufacturer, pid, serial_number, vid, usb_info)
    """
    return [
        {
            'name': p.name,
            'device': p.device,
            'description': p.description,
            'hwid': p.hwid,
            'location': p.location,
            'manufacturer': p.manufacturer,
            'pid': p.pid,
            'serial_number': p.serial_number,
            'vid': p.vid,
            'usb_info': p.usb_info(),
            # 'product': p.product,
            # 'usb_description': p.usb_description(),
            # 'interface': p.interface,
        }
        for p in ls.comports()
        if all or p.pid is not None
    ]


class Conn(ABC):
    __defSlave = {}

    @abstractmethod
    def __init__(self) -> None:
        self.__slaves = {}

    def __call__(self):
        return self.__dict__

    @abstractmethod
    def read(self, slave: int = 0, address: list = []) -> dict:
        """Read all address contented in MIB or only addresse that match address list

        Args:
            slave (int, optional): Number of slave that it wants read data. Defaults to 0.
            address (list, optional): A list of address contented in MIB that it wants read only. Defaults to [] that read all MIB-addr object values.

        Returns:
            dict: Every results asked 'key:value' where value is a object ModbusTypeInteface ex: Int, Short, Dec
        """
        ...

    @abstractmethod
    def write(self, slave: int = 0, address: dict = {}) -> None:
        """Write by connection the values of modbus

        Args:
            slave (int, optional): Number of the slave that it wants write data. Defaults to 0.
            address (dict, optional): Dictionary (key:value) of address contented in MIB that it wants write. Defaults to {} that write all MIB-addr object values.
        """
        ...

    def slave(self, slave: int, mib: dict = {}) -> 'Mib':
        if mib is None or len(mib) == 0:
            return Mib(self.__slaves.get(slave, Conn.__defSlave.get(slave)))
        self.__slaves[slave] = Mib(mib)
        return self.__slaves[slave]

    @staticmethod
    def defSlave(slave: int, mib: dict = {}) -> 'Mib':
        if mib is None or len(mib) == 0:
            if slave in Conn.__defSlave.keys():
                return Conn.__defSlave[slave]
            return Mib()
        Conn.__defSlave[slave] = Mib(mib)
        return Conn.__defSlave[slave]

    def _readMib(self, slave: int, address: list) -> 'tuple[Mib,list,list]':
        mib = self.slave(slave)
        keys = list(mib().keys())
        if address is None or len(address) == 0:
            address = list(mib.value.keys())
        return (mib, keys, address)


class ConnTCP(Conn):
    def __init__(self, host: str, port: int = Defaults.TcpPort) -> None:
        """Collect a list of modbus address in TCP/IP Address

        Args:
            host (str): Ip or hostname to connect in Modbus bus
            port (int, optional): Port of Ip if diferent of default. Defaults to Defaults.TcpPort.
        """
        super().__init__()
        self.host = host
        self.port = port

    def read(self, slave: int = 0, address: list = []) -> dict:
        mib, keys, address = self._readMib(slave, address)

        cli = ModbusTcpClient(self.host, self.port)
        dictFnCode = {
            1: cli.read_coils,
            2: cli.read_discrete_inputs,
            3: cli.read_holding_registers,
            4: cli.read_input_registers,
            # 7: cli.read_exception_status,
            # 14: cli.read_device_information,
            # 20: cli.read_file_record,
            # 24: cli.read_fifo_queue,
        }
        # cli.clear_buffers_before_each_transaction = True
        cli.connect()

        out = {}
        for name in address:
            if name not in keys:
                continue
            o = InitModBusType(mib.value[name], name, slave)
            fn = dictFnCode[o.fnCode]

            result = fn(address=o.addr, count=o.obj.len, slave=slave)
            o.obj.raw = [
                result.getRegister(seq)
                for seq in range(o.obj.len)
            ]
            out[name] = o.obj

        # cli.close_port_after_each_call = True
        cli.close()

        return out

    def write(self, slave: int = 0, address: dict = {}) -> None:
        mib = self.slave(slave)


class ConnRTU(Conn):
    def __init__(self, port: str = 'COM1', baudrate: int = 9600, bytesize: int = 8, parity: str = serial.PARITY_NONE, stopbits: int = 1, timeout: float = 0.1) -> None:
        """Collect a list of modbus address in serial RTU

            Args:
                port (str, optional): Serial port of connection. Use getSerials() to known with to use. Defaults to 'COM1'.
                baudrate (int, optional): Defaults to 9600.
                bytesize (int, optional): Defaults to 8.
                parity (_type_, optional): Defaults to serial.PARITY_NONE.
                stopbits (int, optional): Defaults to 1.
                timeout (float, optional): Defaults to 0.1.
        """
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self._mode = minimalmodbus.MODE_RTU

    def read(self, slave: int = 0, address: list = []) -> dict:
        mib, keys, address = self._readMib(slave, address)

        cli = minimalmodbus.Instrument(
            port=self.port,
            slaveaddress=0,
            mode=self._mode
        )
        cli.serial.baudrate = self.baudrate
        cli.serial.bytesize = self.bytesize
        cli.serial.parity = self.parity
        cli.serial.stopbits = self.stopbits
        cli.serial.timeout = self.timeout
        cli.clear_buffers_before_each_transaction = True

        out = {}
        for name in address:
            if name not in keys:
                continue
            o = InitModBusType(mib.value[name], name, slave)
            cli.address = slave

            if o.fnCode in (1, 2):
                o.obj.raw = cli.read_bits(o.addr, o.obj.bits, o.fnCode)
            elif o.fnCode in (3, 4):
                o.obj.raw = cli.read_registers(o.addr, o.obj.len, o.fnCode)
            out[name] = o.obj

        cli.close_port_after_each_call = True

        return out

    def write(self, slave: int = 0, address: dict = {}) -> dict:
        mib = self.slave(slave)
        return {}


class ConnASCII(ConnRTU):
    def __init__(self, port: str = 'COM1', baudrate: int = 9600, bytesize: int = 8, parity: str = serial.PARITY_NONE, stopbits: int = 1, timeout: float = 0.1) -> None:
        """Collect a list of modbus address in serial ASCII

            Args:
                port (str, optional): Serial port of connection. Use getSerials() to known with to use. Defaults to 'COM1'.
                baudrate (int, optional): Defaults to 9600.
                bytesize (int, optional): Defaults to 8.
                parity (_type_, optional): Defaults to serial.PARITY_NONE.
                stopbits (int, optional): Defaults to 1.
                timeout (float, optional): Defaults to 0.1.
        """
        super().__init__(port, baudrate, bytesize, parity, stopbits, timeout)
        self._mode = minimalmodbus.MODE_ASCII


class Mib:
    def __init__(self, value: 'Mib|dict' = {}) -> None:
        self._count = 0
        if isinstance(value, Mib):
            self.value = value.value
        else:
            self.value = {}
            t = type(value)
            v = {} if value is None or t != dict else value
            for i in v:
                self.add(i, *list(v[i]))

    def __call__(self) -> dict:
        return self.value

    def add(self, name: str, addr: int = 0, fnCode: int = 4, callbackFunction: 'str|tuple|list' = ''):
        if name is None:
            n = self._count
            self._count += 1
        else:
            n = name

        self.value[n] = [addr, fnCode, callbackFunction]


class InitModBusType:
    def __init__(self, lineConfig: 'tuple|list', name='', slave: int = 0) -> None:
        self.name = name
        self.slave = slave

        lineConfig = list(lineConfig)
        t = len(lineConfig)
        d = [0, 4, None]
        for i in range(t, 3):
            lineConfig.append(d[i])

        self.addr = lineConfig[0]
        self.fnCode = lineConfig[1]
        self.obj = self.paser(lineConfig[2])

    def paser(self, className: 'str|list|tuple|mbt.ModbusTypeInteface') -> 'mbt.ModbusTypeInteface':
        if isinstance(className, mbt.ModbusTypeInteface):
            return className
        if type(className) in [list, tuple]:
            c = className[0]
            p = className[1] if len(className) > 1 else {}
            if type(p) != dict or p is None:
                p = {}
        else:
            c = className
            p = {}
        if c == '':
            c = 'Short'
        return getattr(mbt, str(c))(p)
