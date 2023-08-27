#!/usr/bin/python
import os
import sys
import libs
import libs.fingerprint as fingerprint
import argparse

from argparse import RawTextHelpFormatter
from itertools import zip_longest
from termcolor import colored
from libs.config import get_config
from libs.reader_microphone import MicrophoneReader
from libs.visualiser_console import VisualiserConsole as visual_peak
from libs.visualiser_plot import VisualiserPlot as visual_plot
from libs.db_sqlite import SqliteDatabase
# from libs.db_mongo import MongoDatabase

def record_audio_test():
  while True:
    config = get_config()

    db = SqliteDatabase()
    """
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--seconds', nargs='?')
    args = parser.parse_args()
    
    if not args.seconds:
      parser.print_help()
      sys.exit(0)
    """
    seconds = 5

    chunksize = 2**12  # 4096
    channels = 2#int(config['channels']) # 1=mono, 2=stereo

    record_forever = True if seconds == 0 else False
    visualise_console = bool(config['mic.visualise_console'])
    visualise_plot = bool(config['mic.visualise_plot'])

    reader = MicrophoneReader(None)

    if not record_forever:
      reader.start_recording(seconds=seconds,
        chunksize=chunksize,
        channels=channels)
      msg = ' * started recording..'
      print (colored(msg, attrs=['dark']))
    else:
      reader.start_recording(chunksize=chunksize,channels=channels)
      msg = ' * started recording..'
      print (colored(msg, attrs=['dark']))

    while True:
      bufferSize = int(reader.rate / reader.chunksize * seconds)

      for i in range(0, bufferSize):
        nums = reader.process_recording()

        if visualise_console:
          msg = colored('   %05d', attrs=['dark']) + colored(' %s', 'green')
          #print (msg  % visual_peak.calc(nums))
        else:
          msg = '   processing %d of %d..' % (i, bufferSize)
          #print (colored(msg, attrs=['dark']))

      if not record_forever: break

    if visualise_plot:
      data = reader.get_recorded_data()[0]
      visual_plot.show(data)

    reader.stop_recording()
    if not record_forever:
      msg = ' * recording has been stopped'
    else:
      msg = ' * continuous recording has been stopped'
    print (colored(msg, attrs=['dark']))



    def grouper(iterable, n, fillvalue=None):
      args = [iter(iterable)] * n
      return (filter(None, values) for values
              in zip_longest(fillvalue=fillvalue, *args))

    data = reader.get_recorded_data()
    
    msg = ' * recorded %d samples'
    #print (colored(msg, attrs=['dark']) % len(data[0]))
    
    return data
