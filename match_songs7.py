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
#測試
from pydub import AudioSegment
from scipy.io import wavfile
import pyaudio
import numpy
import wave
#from reader import BaseReader  # 你需要导入 BaseReader 类
from libs.audio_reader import AudioFileReader  # 你的修改后的类

def match_songs7(data):
  """
  file_path = wav_file_path  # 替换为你的音频文件路径
  file_reader = AudioFileReader(file_path)
  file_reader.start_reading()
  while not file_reader.recorded:
      audio_data = file_reader.read_chunk()
      if audio_data is None:
          break
      # 在这里执行处理音频数据的操作
  file_reader.stop_reading()
  data = file_reader.get_recorded_data()
  """

  def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in zip_longest(fillvalue=fillvalue, *args))
  """
  def get_record(wav_file_path):
    rate, data = wavfile.read(wav_file_path)
    return rate, data
  rate, data = get_record(wav_file_path)
  """
  config = get_config()

  db = SqliteDatabase()
  
  channel_amount = len(data)
  result = set()
  matches = []

  def find_matches(samples, Fs=fingerprint.DEFAULT_FS):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    return return_matches(hashes)

  def return_matches(hashes):
    mapper = {}
    for hash, offset in hashes:
      mapper[hash.upper()] = offset
    values = mapper.keys()

    for split_values in grouper(values, 1000):
      # @todo move to db related files
      query = """
        SELECT upper(hash), song_fk, offset
        FROM fingerprints
        WHERE upper(hash) IN (%s)
      """
      split_values_list = list(split_values)
      query = query % ', '.join('?' * len(split_values_list))

      x = db.executeAll(query, split_values_list)
      matches_found = len(x)

      if matches_found > 0:
        msg = '   ** found %d hash matches (step %d/%d)'
        #print (colored(msg, 'green') % (
        #  matches_found,
        #  len(split_values_list),
        #  len(values)
        #))
      else:
        msg = '   ** not matches found (step %d/%d)'
        #print (colored(msg, 'red') % (
        #  len(split_values_list),
        #  len(values)
        #))

      for hash, sid, offset in x:
        # (sid, db_offset - song_sampled_offset)
        offset_int=int.from_bytes(offset,byteorder='little',signed = False)
        yield (sid, offset_int - mapper[hash])
  
  
  for channeln, channel in enumerate(data):
    # TODO: Remove prints or change them into optional logging.
    msg = '   fingerprinting channel %d/%d'
    #print (colored(msg, attrs=['dark']) % (channeln+1, channel_amount))

    matches.extend(find_matches(channel))

    msg = '   finished channel %d/%d, got %d hashes'
    #print (colored(msg, attrs=['dark']) % (
    #  channeln+1, channel_amount, len(matches)
    #))

  def align_matches(matches):
    diff_counter = {}
    largest = 0
    largest_count = 0
    song_id = -1

    for tup in matches:
      sid, diff = tup

      if diff not in diff_counter:
        diff_counter[diff] = {}

      if sid not in diff_counter[diff]:
        diff_counter[diff][sid] = 0

      diff_counter[diff][sid] += 1

      if diff_counter[diff][sid] > largest_count:
        largest = diff
        largest_count = diff_counter[diff][sid]
        song_id = sid

    songM = db.get_song_by_id(song_id)

    nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                     fingerprint.DEFAULT_WINDOW_SIZE *
                     fingerprint.DEFAULT_OVERLAP_RATIO, 5)

    return {
        "SONG_ID" : song_id,
        "SONG_NAME" : songM[1],
        "CONFIDENCE" : largest_count,
        "OFFSET" : int(largest),
        "OFFSET_SECS" : nseconds
    }

  total_matches_found = len(matches)

  #print ('')

  if total_matches_found > 5:
    msg = ' ** totally found %d hash matches'
    print (colored(msg, 'green') % total_matches_found)

    song = align_matches(matches)

    msg = ' => song: %s (id=%d)\n'
    msg += '    offset: %d (%d secs)\n'
    msg += '    confidence: %d'

    print (colored(msg, 'green') % (
      song['SONG_NAME'], song['SONG_ID'],
      song['OFFSET'], song['OFFSET_SECS'],
      song['CONFIDENCE']
    ))
    return song['SONG_NAME']
  else:
    msg = ' ** not matches found at all'
    print (colored(msg, 'red'))
    return 'no'
    
#audio = AudioSegment.from_file('wav/audio_1692525324.wav')
#audio_data = audio.raw_data
#match_songs('wav/audio_1692551389.wav')
