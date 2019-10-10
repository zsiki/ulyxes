#!/usr/bin/python

if __name__ == "__main__":
    from leicadnaunit import LeicaDnaUnit
    from serialiface import SerialIface
    from csvwriter import CsvWriter
    from digitallevel import DigitalLevel
    from echowriter import EchoWriter
    
    # wrt = EchoWriter()
    wrt = CsvWriter(angle='DMS', dist='.5f',
                    filt=['id', 'distance', 'staff', 'datetime'],
                    fname='stdout', mode='a', sep=';')
    mu = LeicaDnaUnit()
    iface = SerialIface('x', 'COM3', 9600)
    dna = DigitalLevel('DNA03', mu, iface, wrt)
    dna.SetAutoOff(0)
    #print (dna.GetAutoOff())
    print (dna.Temperature())
    for i in range(10):
        dna.Measure()