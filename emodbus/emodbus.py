from abc import ABC, abstractmethod
import serial
import minimalmodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Defaults
from . import modbustypes as mbt


class Conn(ABC):
    defSlave = {}

    @abstractmethod
    def __init__(self, ) -> None:
        self._slaves = {}

    def __call__(self):
        return self.__dict__

    @abstractmethod
    def read(self, slave: int = 0, address: list = []) -> dict:
        """Read by connection the values of modbus

        Args:
            slave (int, optional): Number of slave that it wants collect data. Defaults to 0.
            address (list, optional): List of keys of mib address to collect only keys. Defaults to [] that collect all MIB.

        Returns:
            dict: return a relation key=>value of all asked
        """
        ...

    @abstractmethod
    def write(self, slave: int = 0, address: dict = {}) -> dict:
        """Write by connection the values of modbus

        Args:
            slave (int, optional): Number of slave that it wants collect data. Defaults to 0.
            address (dict, optional): Dictionary of key=>value of mib address to collect only keys. Defaults to {} that write all MIB object values.

        Returns:
            dict: return a relation key=>value of all asked
        """
        ...

    def slave(self, slave: int, mib: dict = None) -> 'dict|None':
        if mib is None:
            return Addr(self._slaves.get(slave, self.defSlave.get(slave)))
        self._slaves[slave] = Addr(mib)

    def _addrRead(self, address: list, mib: dict) -> list:
        if address is None or len(address) == 0:
            return list(mib.value.keys())
        return address


class ConnTCP(Conn):
    """Collect a list of modbus address in TCP/IP Address

        ### Args:
            dictAddress (dict of tuple(address:int,address:int), optional): _description_. Example {'Addr': (address, address, slave)}.
            host (str, optional): _description_.
        ### Returns:
            dict of str: List of values related with addrs argument
    """

    def __init__(self, host: str, port: int = Defaults.TcpPort) -> None:
        super().__init__()
        self.host = host
        self.port = port

    def read(self, slave: int = 0, address: list = []) -> dict:
        mib = self.slave(slave)
        address = self._addrRead(address, mib)
        d = mib().keys()

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
        cli.clear_buffers_before_each_transaction = True
        cli.connect()

        out = {}
        for name in address:
            if name not in d:
                continue
            o = InitModBusType(mib.value[name], name, slave)
            fn = dictFnCode[o.fnCode]

            result = fn(address=o.addr, count=o.obj.len, slave=slave)
            o.obj.raw = [result.getRegister(seq)
                         for seq in range(o.obj.len)]
            out[name] = o.obj

        cli.close_port_after_each_call = True
        cli.close()

        return out

    def write(self, slave: int = 0, address: dict = {}) -> dict:
        mib = self.slave(slave)


class ConnRTU(Conn):
    """Collect a list of modbus address in serial and slave node

        Args:
            dictAddress (dict of tuple(address:int,address:int), optional): _description_. Example {'Addr': (address, address, slave)}.
            port (str, optional): _description_. Defaults to 'COM1'.
            slave (int, optional): _description_. Defaults to 1.
            baudrate (int, optional): _description_. Defaults to 9600.
            bytesize (int, optional): _description_. Defaults to 8.
            parity (_type_, optional): _description_. Defaults to serial.PARITY_NONE.
            stopbits (int, optional): _description_. Defaults to 1.
            timeout (float, optional): _description_. Defaults to 0.1.
        Returns:
            dict of str: List of values related with addrs argument
     """

    def __init__(self, port: str = 'COM1', baudrate: int = 9600, bytesize: int = 8, parity: str = serial.PARITY_NONE, stopbits: int = 1, timeout: float = 0.1) -> None:
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self._mode = minimalmodbus.MODE_RTU

    def read(self, slave: int = 0, address: list = []) -> dict:
        out = {}
        mib = self.slave(slave)
        address = self._addrRead(address, mib)
        d = mib().keys()

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

        for name in address:
            if name not in d:
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


class ConnASCII(ConnRTU):
    def __init__(self, port: str = 'COM1', baudrate: int = 9600, bytesize: int = 8, parity: str = serial.PARITY_NONE, stopbits: int = 1, timeout: float = 0.1) -> None:
        super().__init__(port, baudrate, bytesize, parity, stopbits, timeout)
        self._mode = minimalmodbus.MODE_ASCII


class Addr:
    def __init__(self, value: 'Addr|dict' = {}) -> None:
        self._count = 0
        self.value = {}
        t = type(value)
        if t == Addr:
            self.value = value.value
        else:
            t = type(value)
            v = {} if value is None or t != dict else value
            for i in v:
                self.add(i, *list(v[i]))

    def __call__(self) -> dict:
        return self.value

    def add(self, name: str = None, addr: int = 0, fnCode: int = 4, callbackFunction: 'str|tuple|list' = None):
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
        t = type(className)
        if t == list or t == tuple:
            c = className[0]
            p = dict(className[1])
        else:
            c = className
            p = {}
        if c is None or type(c) != str and c == '':
            return mbt.Short(p)
        return getattr(mbt, c)(p)
