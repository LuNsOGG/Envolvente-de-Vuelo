from matplotlib.figure import Figure

COLORS=dict(man='#111111',gust='#333333',combined='#000000')

def envelope_figure(result,kind,compact=False,show_reference=False,figure=None):
    fig=figure if figure is not None else Figure(figsize=(10,6.3),dpi=110,layout='constrained')
    if figure is not None:fig.clear()
    fig.get_layout_engine().set(rect=(0,.045,1,.955))
    ax=fig.add_subplot(111)
    ax.set_facecolor('#ffffff');ax.grid(True,color='#dddddd',linewidth=.6)
    titles={'man':'Diagrama V-n de maniobras','gust':'Diagrama V-n de ráfagas','combined':'Envolvente combinada de diseño'}
    subtitle=result['name'] if result.get('requires_thesis',True) else result.get('aircraft','Aeronave')+' · '+result['name']
    ax.set_title(titles[kind]+('' if compact or result.get('worksheet') else '\n'+subtitle),loc='left',fontsize=10 if compact else 13,pad=8 if compact else 12)
    ax.set_xlabel('Velocidad equivalente V [kt EAS]');ax.set_ylabel('Factor de carga n [1]')
    if compact:
        ax.xaxis.label.set_size(8);ax.yaxis.label.set_size(8);ax.tick_params(labelsize=7)
    ax.axhline(0,color='#555555',lw=.8);ax.axhline(1,color='#aaaaaa',lw=.7,ls=':')
    c=result['curves'];v=c.get('V',[])
    key={'man':'man','gust':'gust','combined':'combined'}[kind]
    if key+'_pos' not in c:
        pending=result.get('blocked',[])
        if result.get('worksheet') and result.get('method')!='niu':
            pending={'man':['CN mínimo negativo pendiente'],
                     'gust':['Datos de ráfaga pendientes'],
                     'combined':['Datos de maniobra o ráfaga pendientes']}[kind]
        text='CÁLCULO PENDIENTE\n'+'\n'.join(pending[:3 if compact else 6])
        ax.text(.5,.5,text,transform=ax.transAxes,ha='center',va='center',fontsize=8 if compact else 11,wrap=True)
        if result.get('worksheet'):
            values=result.get('values',{})
            if values.get('Vd',0)>0:ax.set_xlim(0,values['Vd']*1.04)
            if values.get('n_pos',0)>0:ax.set_ylim(min(-2,values.get('n_neg',-2)-.5),max(4,values['n_pos']+.8))
        return fig
    if kind=='combined':
        for prefix,label,color in [('man','Maniobras','#888888'),('gust','Ráfagas sin recorte','#555555')]:
            if prefix+'_pos' in c:
                style='--' if prefix=='man' else '-.'
                ax.plot(v,c[prefix+'_pos'],ls=style,color=color,lw=1.1,label=label)
                ax.plot(v,c[prefix+'_neg'],ls=style,color=color,lw=1.1)
    p=c[key+'_pos'];m=c[key+'_neg'];color=COLORS[kind]
    ax.plot(v,p,color=color,lw=2.2,label={'man':'Frontera de maniobra','gust':'Condiciones de ráfaga','combined':'Contorno combinado'}[kind])
    ax.plot(v,m,color=color,lw=2.2)
    if all(x is not None for x in p+m):
        if kind!='gust':ax.fill_between(v,m,p,color=color,alpha=.13)
        ax.plot([v[-1],v[-1]],[m[-1],p[-1]],color=color,lw=1.7)
    if kind!='gust':
        for s,lbl in [('stall_pos','Límite de pérdida estática'),('stall_neg',None)]:
            if s in c:
                xs=[x for x,y in zip(v,c[s]) if abs(y)<max(6,max(p)+1)]
                ys=[y for y in c[s] if abs(y)<max(6,max(p)+1)]
                ax.plot(xs,ys,color='#999999',ls=':',lw=1,label=lbl)
    if all(x is not None for x in p+m):ax.set_ylim(min(-2,min(m)-.55),max(4,max(p)+.8))
    elif result.get('partial',{}).get(kind):ax.set_ylim(min(-2,result['values'].get('n_neg',-2)-.5),max(4,max(p)+.8))
    speed_labels=[('Vs','Vs'),('V_A_stall','A'),('Vc','Vc'),('Vd','Vd')] if compact else [('Vs','Vs'),('V_A_stall','A'),('Va','Va sel.'),('Vc','Vc'),('Vd','Vd')]
    if result.get('method')=='niu':
        speed_labels=[('Vs','Vs'),('Vb','VB') if kind!='man' and 'Vb' in result['values'] else ('V_A_stall','A'),('Vc','Vc'),('Vd','Vd')]
    if 'Va_selected' in result.get('values',{}):
        if not compact:speed_labels.insert(2,('Va_selected','Va sel.'))
    for i,(key2,label) in enumerate(speed_labels):
        x=result['values'].get(key2)
        if x is None:continue
        ax.axvline(x,color='#888888',ls=':',lw=.7)
        label_y=.72 if label=='Vs' else .95-(i%2)*.11
        ax.text(x,label_y,f'{label} {x:.1f}',transform=ax.get_xaxis_transform(),ha='right' if label=='Vd' else 'center',fontsize=6 if compact else 8,color='#333333',bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=2))
    ax.set_xlim(0,max(v)*1.04)
    if kind=='man' and not compact:
        for pt in result['points']:
            if pt['punto'] in ['A','G','D','E']:
                ax.scatter(pt['V'],pt['n'],color=color,s=20,zorder=4)
                label=pt['punto']+(f' (n={pt["n"]:.2f})' if pt['punto'] in ['A','G'] else '')
                ax.annotate(label,(pt['V'],pt['n']),xytext=(6,-16 if pt['punto']=='G' else 8),textcoords='offset points',fontsize=9)
    if kind=='gust' and not compact:
        for side,yoff in [('pos',20),('neg',-15)]:
            val=result['values'].get('n_gust_c_'+side)
            if val is not None:ax.annotate(f'n={val:.3f}',(result['values']['Vc'],val),xytext=(7,yoff),textcoords='offset points',fontsize=9,color=color)
    if show_reference and result.get('reference_curves'):
        ref=result['reference_curves'];ax.plot(ref['V'],ref[kind+'_pos'],ls='--',color='#777777',lw=1.4,label='Tesis publicada · referencia')
        ax.plot(ref['V'],ref[kind+'_neg'],ls='--',color='#777777',lw=1.4)
    # Incluye todas las curvas visibles, también demanda sin recorte y referencia.
    import math
    visible_y=[float(y) for line in ax.lines for y in line.get_ydata() if y is not None and math.isfinite(float(y))]
    visible_x=[float(x) for line in ax.lines for x in line.get_xdata() if x is not None and math.isfinite(float(x))]
    if visible_y:ax.set_ylim(min(-2,min(visible_y)-.55),max(4,max(visible_y)+.8))
    if visible_x:ax.set_xlim(0,max(visible_x)*1.04)
    ax.legend(loc='upper left',fontsize=6 if compact else 8,framealpha=.95)
    if result.get('partial',{}).get(kind):
        ax.text(.98,.035,result['partial'][kind],transform=ax.transAxes,ha='right',fontsize=7 if compact else 9,
                bbox=dict(facecolor='white',edgecolor='#777777',alpha=.95,pad=3))
    if result.get('academic_notice'):
        fig.text(.99,.003,'Uso académico · Aproximación estática · '+('Apéndice A: AR>7' if result['values'].get('AR',0)>7 else 'Aplicabilidad pendiente'),ha='right',fontsize=6 if compact else 8,color='#555555')
    if not compact and not result.get('worksheet'):
        footer='Uso académico · Datos e hipótesis en el reporte'
        if result.get('requires_thesis',False):footer+=' · Variante pendiente de tesis'
        fig.text(.99,.005,footer,ha='right',fontsize=8,color='#666666')
    return fig

def export_plots(result,directory,progress=None):
    paths={}
    for k in ['man','gust','combined']:
        if progress:progress(k)
        fig=envelope_figure(result,k)
        for ext in ['png','svg']:
            path=directory/f'{k}.{ext}';fig.savefig(path,dpi=260,bbox_inches='tight')
            paths[k+'_'+ext]=path
    return paths
