#!/usr/bin/env python3
"""Caixa de entrada do app: o Claude escreve compromissos criptografados em inbox.json.

Só quem tem a chave privada (guardada no Firebase do dono) consegue ler.

Uso:
  python3 tools/inbox.py add --title "Dentista" --date 2026-10-12 [--time 15:00]
                             [--pillar saude|namorado|filho|organizado]
                             [--recur none|daily|weekly|monthly|lastwd|semiannual|yearly]
                             [--notes "..."] [--programa] [--id meu-id]
  python3 tools/inbox.py del --id ID
  python3 tools/inbox.py list        # mostra só ids e datas de envio (o conteúdo é ilegível)
"""
import argparse, base64, json, os, re, time, unicodedata
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'tools', 'claude_pubkey.txt')
BOX = os.path.join(ROOT, 'inbox.json')
PILLARS = {'saude', 'namorado', 'filho', 'organizado'}
RECUR = {'none', 'daily', 'weekly', 'monthly', 'lastwd', 'semiannual', 'yearly'}


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:40] or 'ev'


def encrypt(msg):
    der = base64.b64decode(open(PUB).read().strip())
    pub = serialization.load_der_public_key(der)
    key = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    c = AESGCM(key).encrypt(iv, json.dumps(msg, ensure_ascii=False).encode(), None)
    k = pub.encrypt(key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    b = lambda x: base64.b64encode(x).decode()
    return {'k': b(k), 'iv': b(iv), 'c': b(c)}


def load():
    if os.path.exists(BOX):
        return json.load(open(BOX))
    return {'items': []}


def save(box):
    box['items'] = box['items'][-300:]
    json.dump(box, open(BOX, 'w'), indent=1)
    open(BOX, 'a').write('\n')


def push(msg):
    box = load()
    item = {'id': 'm' + str(int(time.time() * 1000)), 'at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    item.update(encrypt(msg))
    box['items'].append(item)
    save(box)
    return item['id']


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add')
    a.add_argument('--title', required=True)
    a.add_argument('--date', required=True, help='AAAA-MM-DD')
    a.add_argument('--time', default='')
    a.add_argument('--pillar', default='organizado', choices=sorted(PILLARS))
    a.add_argument('--recur', default='none', choices=sorted(RECUR))
    a.add_argument('--notes', default='')
    a.add_argument('--programa', action='store_true')
    a.add_argument('--id')
    d = sub.add_parser('del')
    d.add_argument('--id', required=True)
    sub.add_parser('list')
    x = ap.parse_args()

    if x.cmd == 'list':
        for it in load()['items']:
            print(it['id'], it.get('at', ''))
        return
    if x.cmd == 'del':
        mid = push({'op': 'del', 'id': x.id})
        print('removido', x.id, 'msg', mid)
        return
    datetime.strptime(x.date, '%Y-%m-%d')
    if x.time:
        datetime.strptime(x.time, '%H:%M')
    eid = x.id or ('c-' + slug(x.title) + '-' + x.date)
    ev = {'id': eid, 'title': x.title, 'date': x.date, 'time': x.time, 'pillar': x.pillar,
          'recur': x.recur, 'kind': 'programa' if x.programa else '', 'notes': x.notes}
    mid = push({'op': 'add', 'ev': ev})
    print('adicionado', eid, 'msg', mid)


if __name__ == '__main__':
    main()
