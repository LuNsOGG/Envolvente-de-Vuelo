"""Punto de entrada de escritorio y de reproducción sin interfaz."""
import bootstrap
from bootstrap import ROOT
import argparse
import sys

def main():
    p=argparse.ArgumentParser(description='Envolvente de vuelo académica en español')
    p.add_argument('--project',default=None)
    p.add_argument('--case',default=None)
    p.add_argument('--export',action='store_true')
    p.add_argument('--all',action='store_true',help='Exportar todas las condiciones')
    p.add_argument('--niu',action='store_true',help='Generar solo reporte independiente de Niu')
    p.add_argument('--screenshot',default=None,help=argparse.SUPPRESS)
    p.add_argument('--comprobar',action='store_true',help='Comprobar cálculo, guardado y tres gráficas del ejecutable')
    p.add_argument('--comprobar-gui',action='store_true',help='Comprobar edición y recálculo en la interfaz')
    args=p.parse_args()
    from src.project import load_project
    from src.calculations.worksheet import worksheet_project
    project=load_project(args.project) if args.project else worksheet_project()
    if args.comprobar or args.comprobar_gui:
        from src.worksheet_selfcheck import run_selfcheck
        run_selfcheck(gui=args.comprobar_gui)
        return 0
    if args.case:
        if args.case not in [c['id'] for c in project['cases']]:p.error('Caso desconocido')
        project['active_case']=args.case
    if args.export or args.all or args.niu:
        import matplotlib
        matplotlib.use('Agg')
        from src.reporting.exporter import export_project
        print(export_project(project,project['active_case'],all_cases=args.all,niu_only=args.niu))
        return 0
    from src.ui.worksheet import launch
    return launch(project,args.screenshot)

if __name__=='__main__':sys.exit(main())
