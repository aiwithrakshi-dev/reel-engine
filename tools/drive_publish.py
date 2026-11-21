#!/usr/bin/env python3
"""Upload a reel package (tools/reel_package.py) to Google Drive:

  Social Media / 2026-11 November / Day 21 - 2026-11-21 / <reel title> /
      <slug>_60fps.mp4, <slug>_thumbnail.jpg, <slug>_thumbnail_grid.jpg,
      <title> — Caption (Google Doc), <title> — Timeline (Google Doc), <title> — QC report (Google Doc)

  python3 tools/drive_publish.py pkg/                 # upload, print folder link, log to memory
  python3 tools/drive_publish.py pkg/ --dry-run       # show what would be created
  python3 tools/drive_publish.py --sync-memory        # upload memory/CONTEXT.md as the "Reel Engine — Memory" Doc

Auth (once per machine): create an OAuth "Desktop app" client in Google Cloud (Drive API enabled), save it as
~/.reel_engine/credentials.json; the first run opens a browser and stores ~/.reel_engine/token.json.
Service account alternative: REEL_DRIVE_SA=/path/key.json (share the Social Media folder with the SA email).
Inside Claude (no local auth): the agent does the same steps with the Google Drive connector — see the template skill.
Folders are found-or-created by exact name, so re-running never duplicates the tree. Re-uploading a file of the same
name in the same folder updates it in place.
"""
import os, sys, json, argparse
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CFG = os.path.expanduser('~/.reel_engine'); SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER = 'application/vnd.google-apps.folder'; DOC = 'application/vnd.google-apps.document'


def service():
    from googleapiclient.discovery import build
    sa = os.environ.get('REEL_DRIVE_SA')
    if sa:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(sa, scopes=SCOPES)
    else:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        tok = os.path.join(CFG, 'token.json'); creds = Credentials.from_authorized_user_file(tok, SCOPES) if os.path.exists(tok) else None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
            else: creds = InstalledAppFlow.from_client_secrets_file(os.path.join(CFG, 'credentials.json'), SCOPES).run_local_server(port=0)
            os.makedirs(CFG, exist_ok=True); open(tok, 'w').write(creds.to_json())
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def q(s): return s.replace("\\", "\\\\").replace("'", "\\'")


def find(svc, name, parent, mime=None):
    qq = f"name = '{q(name)}' and trashed = false and '{parent}' in parents" + (f" and mimeType = '{mime}'" if mime else '')
    r = svc.files().list(q=qq, fields='files(id,name,webViewLink)', spaces='drive').execute().get('files', [])
    return r[0] if r else None


def folder(svc, name, parent):
    f = find(svc, name, parent, FOLDER)
    return f or svc.files().create(body=dict(name=name, mimeType=FOLDER, parents=[parent]), fields='id,name,webViewLink').execute()


def upload(svc, path, name, parent, mime, as_doc=False):
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(path, mimetype=mime, resumable=os.path.getsize(path) > 5_000_000)
    old = find(svc, name, parent)
    if old: return svc.files().update(fileId=old['id'], media_body=media, fields='id,name,webViewLink').execute()
    body = dict(name=name, parents=[parent]); body.update(mimeType=DOC) if as_doc else None
    return svc.files().create(body=body, media_body=media, fields='id,name,webViewLink').execute()


def publish(pkg, dry=False):
    man = json.load(open(os.path.join(pkg, 'manifest.json')))
    if dry:
        print(' / '.join(man['drive_path']))
        for f in man['files']: print('   ', f.get('doc_title') or f['path'], '(Google Doc)' if f.get('doc_title') else '')
        return None
    svc = service(); parent = 'root'
    for name in man['drive_path']: fo = folder(svc, name, parent); parent = fo['id']
    links = {}
    for f in man['files']:
        doc = bool(f.get('doc_title')); mime = 'text/html' if f['mime'] == 'text/html' else ('text/plain' if doc else f['mime'])
        r = upload(svc, os.path.join(pkg, f['path']), f.get('doc_title') or f['path'], parent, mime, as_doc=doc)
        links[f['kind']] = r.get('webViewLink'); print('  up', r['name'])
    links['folder'] = fo.get('webViewLink'); man['drive'] = links
    json.dump(man, open(os.path.join(pkg, 'manifest.json'), 'w'), indent=1)
    sys.path.insert(0, os.path.dirname(__file__)); import memory
    memory.log_reel(man); memory.write_context()
    print('folder:', links['folder']); return links


def sync_memory():
    svc = service(); root = folder(svc, 'Social Media', 'root')
    r = upload(svc, os.path.join(ROOT, 'memory', 'CONTEXT.md'), 'Reel Engine — Memory', root['id'], 'text/plain', as_doc=True)
    print('memory doc:', r.get('webViewLink'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('pkg', nargs='?'); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--sync-memory', action='store_true'); a = ap.parse_args()
    if a.sync_memory: sync_memory()
    else: publish(a.pkg, a.dry_run)
