import sys
from workflow import Workflow3, web

query = sys.argv[1]

url_explorer = "https://blockstream.info/" + query
url_address = "https://blockstream.info/api/address/" + query
url_tx = "https://blockstream.info/api/tx/" + query + "/status"
url_tip = "https://blockstream.info/api/blocks/tip/height"

def get_balance():
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

  return str(bal_in_btc)

def get_tx_confirmations():
  # get tx info
  r = web.get(url_tx)

  # get current tip of main chain
  t = web.get(url_tip)

  # alert alfred if result returns error
  r.raise_for_status()
  t.raise_for_status()

  # parse json
  tip = t.json()
  conf = r.json()

  # tx confirmation check
  if conf['confirmed']:
    # Calculate diff between tip and block height of confirmed tx.
    # Add one to include the confirmed block in the calculation
    conf_count = tip - conf['block_height'] + 1

  else:
    conf_count = 0

  # format confirmation text singular vs plural
  if conf_count == 1:
    return str(conf_count) + ' confirmation'
  else:
    return str(conf_count) + ' confirmations'

def main(wf):
  # check if query is addr or tx
  if len(query) == 64:
    confs = get_tx_confirmations()
    title = confs + ' for TXID: ' + query
    subtitle = 'Confirmations'

  else:
    balance = get_balance()
    title = balance + ' BTC in ' + query
    subtitle = 'Balance'

  # display item for alfred dropdown
  wf.add_item(title=title,
              subtitle=subtitle,
              arg=url_explorer,
              valid=True)

  # send workflow back to alfred as XML
  wf.send_feedback()

if __name__ == "__main__":
     wf = Workflow3()
     sys.exit(wf.run(main))