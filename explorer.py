import sys
from lib.workflow import Workflow3, web

# input
query = sys.argv[1]

# urls to query
url_address = "https://blockstream.info/api/address/" + query
url_tx = "https://blockstream.info/api/tx/" + query
url_tip = "https://blockstream.info/api/blocks/tip/height"

# default subtitle text
url_subtitle = 'Go to Block Explorer and copy to clipboard'
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

  url_subtitle = ''

  address_title = 'Address: ' + query
  balance_title = 'Balance: ' + str(bal_in_btc) + 'BTC'

  address_info = [
    {'title': address_title, 'subtitle': address_subtitle},
    {'title': balance_title, 'subtitle': balance_subtitle}
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
  tx = r.json()
  tip = t.json()

  # extract data
  confirmation = tx['status']
  fee = str(tx['fee'] * .00000001)
  size = str(tx['size'])
  weight = str(tx['weight'])

  # tx confirmation check
  # Calculate diff between tip and block height of confirmed tx.
  # Add one to include the confirmed block in the calculation
  if confirmation['confirmed']:
    conf_count = str(tip - confirmation['block_height'] + 1)
  else:
    conf_count = '0'

  # alfred item info
  id_title = 'TXID: ' + query
  id_arg = query

  conf_title = 'Confirmations: ' + conf_count
  conf_arg = conf_count

  fee_title = 'Fee: ' + fee + ' BTC'
  fee_arg = fee

  size_title = 'Size: ' + size + 'b'
  size_arg = size

  weight_title = 'Weight: ' + weight + 'wu'
  weight_arg = weight

  tx_info = [
    {'title': id_title, 'subtitle': url_subtitle, 'arg': id_arg},
    {'title': conf_title, 'subtitle': subtitle, 'arg': conf_arg},
    {'title': fee_title, 'subtitle': subtitle, 'arg': fee_arg},
    {'title': size_title, 'subtitle': subtitle, 'arg': size_arg},
    {'title': weight_title, 'subtitle': subtitle, 'arg': weight_arg},
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