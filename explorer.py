import sys
from lib.workflow import Workflow3, web

# input
query = sys.argv[1]

# urls to query
url_address = "https://blockstream.info/api/address/" + query
url_tx = "https://blockstream.info/api/tx/" + query
url_tip = "https://blockstream.info/api/blocks/tip/height"

# default subtitle text
url_subtitle = 'Copy info to clipboard and go to Block Explorer'
subtitle = 'Copy amount to clipboard'

def get_address():
  # get address info
  r = web.get(url_address)

  # alert alfred if result error
  r.raise_for_status()

  # parse json and pull out chain_stats
  data = r.json()['chain_stats']

  # calculate balance
  bal_in_sat = data['funded_txo_sum'] - data['spent_txo_sum']

  # convert from sats to bitcoin
  bal_in_btc = bal_in_sat * .00000001

  # convert to string
  balance = str(bal_in_btc)

  #titles
  address_title = 'Address: ' + query
  balance_title = 'Balance: ' + balance + 'BTC'

  address_info = [
    {'title': address_title, 'subtitle': url_subtitle, 'arg': query},
    {'title': balance_title, 'subtitle': subtitle, 'arg': balance},
  ]

  return address_info

def get_tx():
  # get tx info
  r = web.get(url_tx)

  # get current tip of main chain
  t = web.get(url_tip)

  # alert alfred if result returns error
  r.raise_for_status()
  t.raise_for_status()

  # parse json
  tip = t.json()
  tx = r.json()

  # extract data
  confirmation = tx['status']
  size = str(tx['size'])
  weight = str(tx['weight'])

  # Virtual size (vsize), also called virtual bytes (vbytes),
  # are an alternative measurement, with one vbyte being equal
  # to four weight units. That means the maximum block size
  # measured in vsize is 1 million vbytes.
  v_size = tx['weight'] / 4

  sat_per_byte = str(tx['fee']/v_size)
  fee_in_btc = tx['fee'] * .00000001
  format_fee = "{:.8f}".format(float(fee_in_btc))
  fee = str(format_fee) + ' BTC' + ' ('+ sat_per_byte + ' sat/B)'

  # tx confirmation check
  # Calculate diff between tip and block height of confirmed tx.
  # Add one to include the confirmed block in the calculation
  if confirmation['confirmed']:
    conf_count = str(tip - confirmation['block_height'] + 1)
  else:
    conf_count = '0'

  # alfred item info
  id_title = 'TXID: ' + query
  conf_title = 'Confirmations: ' + conf_count
  fee_title = 'Fee: ' + fee
  size_title = 'Size: ' + size + 'b'
  weight_title = 'Weight: ' + weight + 'wu'

  tx_info = [
    {'title': id_title, 'subtitle': url_subtitle, 'arg': query},
    {'title': conf_title, 'subtitle': subtitle, 'arg': conf_count},
    {'title': fee_title, 'subtitle': subtitle, 'arg': fee},
    {'title': size_title, 'subtitle': subtitle, 'arg': size},
    {'title': weight_title, 'subtitle': subtitle, 'arg': weight},
  ]

  return tx_info

def add_item(arr):
  for item in arr:
    wf.add_item(title=item['title'],
                subtitle=item['subtitle'],
                arg=item['arg'],
                valid=True)

def main(wf):
  # check if query is addr or tx
  if len(query) == 64:
    add_item(get_tx())
  else:
    add_item(get_address())

  # send workflow back to alfred as XML
  wf.send_feedback()

if __name__ == "__main__":
     wf = Workflow3()
     sys.exit(wf.run(main))