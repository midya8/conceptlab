"""UTF-8 JSON CLI. Output replacement occurs only after successful validation."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import audit
from .partial import audit_partial
from .exploration import explore
from .exploration_verify import verify_exploration


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description='Exact bounded formal concept and implication witnesses')
    p.add_argument('input',help='JSON path or - for stdin')
    p.add_argument('-o','--output',help='output JSON path; default stdout')
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--exploration',action='store_true',help='simulate attribute exploration over a supplied exact context')
    modes.add_argument('--verify-exploration',action='store_true',help='independently reconstruct an exported exploration report')
    modes.add_argument('--partial',action='store_true',help='enumerate bounded 0/1/null matrix completions and implication goals')
    args=p.parse_args(argv)
    try:
        raw=sys.stdin.buffer.read(4194305) if args.input=='-' else Path(args.input).read_bytes()
        if len(raw)>(4194304 if args.verify_exploration else 65536):
            raise ValueError('input exceeds mode UTF-8 byte limit')
        data=json.loads(raw.decode('utf-8'),object_pairs_hook=unique_object,
                        parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON constant')))
        if args.verify_exploration:
            verify_exploration(data)
            result={'valid':True,'schema':'conceptlab-exploration-v1'}
        else:
            result=explore(data) if args.exploration else audit_partial(data) if args.partial else audit(data)
        text=json.dumps(result,ensure_ascii=True,allow_nan=False,indent=2)+'\n'
        if args.output:
            target=Path(args.output)
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=target.parent,delete=False) as f:
                tmp=f.name
                try:f.write(text)
                except BaseException:
                    os.unlink(tmp)
                    raise
            try:os.replace(tmp,target)
            except BaseException:
                os.unlink(tmp)
                raise
        else:sys.stdout.write(text)
    except (ValueError,OSError,UnicodeError,RecursionError) as e:
        p.exit(2,'Invalid input: '+str(e)+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
