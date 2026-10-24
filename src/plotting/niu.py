"""Redibujos técnicos originales basados en páginas inspeccionadas del PDF.

Coordenadas ilustrativas: no son datos de un Cessna ni copias de las imágenes.
"""
from matplotlib.figure import Figure
from matplotlib.patches import Polygon,Ellipse,Arc,Rectangle
import numpy as np

FIGURES=[
 dict(number='3.1.3',title='Typical fighter wing maneuvering flight path vs. wing load cases.',page=22,viewer=29,
      spanish='Trayectoria de maniobra y casos básicos de carga del ala de un caza',
      explanation='El inciso a relaciona posiciones de la aeronave durante ascenso, recuperación y picada con casos de carga. L es la sustentación normal al movimiento y W es el peso, siempre vertical. El inciso b representa n frente al coeficiente de sustentación del ala, no frente a la velocidad. A y A\' alcanzan n máximo; B representa 0.5 n máximo; C tiene coeficiente nulo; D y D\' corresponden a factores negativos. Las regiones I a IV muestran combinaciones de coeficiente y carga.',
      symbols='L: sustentación; W: peso; n: factor de carga; CL: coeficiente del ala; A, A\', B, C, D, D\': casos de carga.',
      simplification='Se esquematiza la trayectoria con segmentos suaves y se normalizan n y CL. Se conservan ambas partes, los signos y la correspondencia entre casos; no es una trayectoria calculada.'),
 dict(number='3.3.1',title='Typical airplane pitching maneuver.',page=33,viewer=40,
      spanish='Maniobra típica de cabeceo',
      explanation='La trayectoria curva cambia la orientación y las cargas normales del avión. La parte a incluye sustentación del ala, carga de cola, empuje, resistencia, peso y la fuerza centrífuga en la representación de equilibrio de D\'Alembert. La parte b muestra cómo cambia la distribución de presión. En una formulación inercial se usa la aceleración en lugar de sumar otra fuerza centrífuga real.',
      symbols='Lw: sustentación del ala; Lt: carga de cola; T: empuje; D: resistencia; W: peso; Fi: fuerza de inercia.',
      simplification='Se dibujan tres estados representativos y curvas de presión cualitativas. Las magnitudes y las distancias son ilustrativas; no se omite el papel de la cola en el equilibrio.'),
 dict(number='3.3.2',title='Airplane in balanced flight.',page=34,viewer=41,
      spanish='Avión en vuelo equilibrado',
      explanation='En vuelo compensado el momento aerodinámico total alrededor del centro de gravedad es nulo o se considera despreciable la aceleración angular. La sustentación de ala y fuselaje, aplicada en el centro aerodinámico, produce un momento por su separación respecto al centro de gravedad. La carga de cola, con brazo lt, equilibra ese momento y el momento aerodinámico del conjunto ala y fuselaje. Puede existir equilibrio a n distinto de uno.',
      symbols='CG: centro de gravedad; AC: centro aerodinámico; Lwb: sustentación de ala y fuselaje; nW: carga de equilibrio; xs y lt: brazos; Mwb: momento aerodinámico.',
      simplification='Avión como cuerpo rígido en vista lateral; se representan cargas resultantes. La ecuación de momentos emplea la convención de flechas dibujada.'),
 dict(number='3.3.3',title='Force diagram due to deflected elevator.',page=34,viewer=41,
      spanish='Fuerzas debidas a la deflexión del elevador',
      explanation='Al mover rápidamente el elevador aparece una carga incremental de cola, ΔT, antes de alcanzar otro equilibrio. El momento resultante causa aceleración angular de cabeceo y queda ligado a la inercia Iyy. Las cargas de sustentación, peso y cola de 1 g se distinguen del incremento que inicia la rotación. No debe imponerse suma de momentos igual a cero durante esa fase.',
      symbols='ΔT: incremento de fuerza de cola, no empuje; lt: brazo de cola; Iyy: momento de inercia en cabeceo; θ doble punto: aceleración angular.',
      simplification='Se aísla el efecto instantáneo del elevador; la respuesta temporal y el cambio posterior de sustentación no se calculan.'),
 dict(number='3.3.4',title='Forces due to deflected ailerons.',page=34,viewer=41,
      spanish='Fuerzas debidas a la deflexión de alerones',
      explanation='La deflexión diferencial de alerones cambia la fuerza normal en cada semiala con signos opuestos. El par de estas fuerzas produce aceleración de alabeo alrededor del eje longitudinal. El momento neto se relaciona con Ixx y p punto. Durante alabeo acelerado, un punto a distancia y1 del eje experimenta un incremento de carga proporcional a p punto por y1 dividido entre g.',
      symbols='ΔFail: incremento de fuerza de alerón; y: brazo de la fuerza; y1: coordenada de un punto; p: velocidad angular de alabeo; Ixx: inercia longitudinal.',
      simplification='Vista frontal y distribución de fuerza reducida a dos resultantes. El par se escribe como 2 ΔF y si y es el brazo de cada fuerza; así se evita confundirlo con una fuerza diferencial ya sumada.'),
 dict(number='3.4.8',title='Significance of the V-n diagram.',page=42,viewer=49,
      spanish='Significado del diagrama V n',
      explanation='Las parábolas de sustentación positiva y negativa delimitan la capacidad aerodinámica estática. Las líneas de carga límite y última distinguen regiones de posible daño permanente y de falla estructural. La línea vertical representa la velocidad límite de la figura. Estar por debajo de una línea última no autoriza operar por encima de la carga límite.',
      symbols='V: velocidad indicada de la figura; n: factor de carga; límite: carga de diseño; última: carga multiplicada por el factor de seguridad aplicable.',
      simplification='Escalas normalizadas sin valores operativos. Se usa 1.5 como relación ilustrativa entre límite y última; los umbrales reales dependen del diseño.'),
 dict(number='3.4.9',title='Typical V-n Diagram for Maneuver.',page=42,viewer=49,
      spanish='Diagrama típico V n de maniobra',
      explanation='La curva de pérdida positiva llega al máximo factor de carga en VA. El contorno superior continúa a VC y VD. La rama negativa alcanza su límite y luego, en el esquema mostrado, asciende hasta n igual a cero en VD. La figura incluye una rama de flaps extendidos y seis condiciones de ángulo de ataque. La velocidad equivalente Ve se relaciona con la verdadera mediante la raíz de la razón de densidades.',
      symbols='PHA, PIA, PLA: ángulo de ataque positivo alto, intermedio y bajo; NHA, NIA, NLA: negativos alto, intermedio y bajo; Vs, VA, VC, VD: velocidades características.',
      simplification='Se conserva la geometría de la rama negativa del original, sin trasladarla automáticamente al apéndice A. La rama de flaps es cualitativa y no define un valor de VF para Cessna.'),
 dict(number='3.4.11',title='Gust load factor nomogram.',page=45,viewer=52,
      spanish='Nomograma de factor de carga por ráfaga',
      explanation='El nomograma relaciona pendiente de sustentación por radián, carga alar, ráfaga derivada, velocidad equivalente, factor de alivio e incremento de carga. La constante 498 requiere W/S en lbf/ft², Ude en ft/s y Ve en nudos. El resultado es Δn; las cargas completas son 1 más o menos ese incremento. Un factor Kg menor que uno reduce la respuesta cuasiestática respecto al caso sin alivio.',
      symbols='a: pendiente por radián; W/S: carga alar; Ude: ráfaga derivada; Ve: velocidad equivalente; Kg: alivio; Δn: incremento de carga.',
      simplification='Redibujo funcional en tres nomogramas de ejes paralelos logarítmicos calibrados, equivalente a la fórmula del original. Se sustituyen sus escalas quebradas por ejes de productos y cocientes; el ejemplo numérico es propio.'),
 dict(number='3.4.16',title='Combined flight envelope (V-n diagram) - fighter.',page=54,viewer=61,
      spanish='Envolvente combinada de vuelo de un caza',
      explanation='Se superponen condiciones de maniobra y ráfaga para identificar los extremos de carga a lo largo del intervalo de velocidades. Las rectas de ráfaga parten de n igual a uno y se consideran sus intersecciones con la capacidad de sustentación. VB, VC y VD identifican regímenes de ráfaga y de velocidad; los perfiles que acompañan al original indican ángulos de ataque y momentos de cabeceo positivos o negativos. Es un esquema de caza y no fija los parámetros de un avión ligero.',
      symbols='VB: velocidad de diseño de ráfaga; VC: crucero; VD: picada; M: momento de cabeceo; CL: coeficiente de sustentación; α: ángulo de ataque.',
      simplification='Envolvente y perfiles esquemáticos normalizados, sin afirmar intensidades normativas de caza. Los perfiles se reducen a signos de α y M, conservados conforme al original.'),
 dict(number='3.5.6',title='Critical conditions for wing box structure.',page=56,viewer=63,
      spanish='Condiciones críticas para la caja alar',
      explanation='Las cuatro combinaciones de ángulo de ataque positivo o negativo, alto o bajo, cambian el momento de flexión y torsión y la posición de la máxima tensión y compresión. El dibujo original indica: esquina superior delantera, compresión en +HAA y tensión en -LAA; superior trasera, compresión en +LAA y tensión en -HAA; inferior delantera, tensión en +LAA y compresión en -HAA; inferior trasera, tensión en +HAA y compresión en -LAA. Cada larguerillo o ala de larguero debe revisarse para sus máximos de tensión y compresión en todos esos casos.',
      symbols='HAA: ángulo de ataque alto; LAA: ángulo de ataque bajo; signos + y -: sentido del ángulo; tensión y compresión: estados longitudinales de los elementos de la caja.',
      simplification='Se dibuja una sección de caja con cuatro esquinas representativas y cuatro orientaciones de perfil. No se presupone que toda la piel superior o inferior tenga el mismo caso crítico.')
]

def arrow(ax,start,end,label='',color='#226e91',offset=(.02,.03)):
    ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='-|>',color=color,lw=1.6))
    if label:ax.text(end[0]+offset[0],end[1]+offset[1],label,fontsize=9,color=color)

def plane(ax,x,y,scale=.2,angle=0):
    # Nariz a la izquierda; cola a la derecha.
    points=np.array([[-1,0],[-.55,.12],[.45,.1],[.7,.4],[.8,.4],[.8,.04],[1,0],[1,-.07],[-.55,-.08]])*scale
    t=np.radians(angle);R=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
    pts=points@R.T+[x,y];ax.add_patch(Polygon(pts,closed=True,facecolor='#e8eff3',edgecolor='#203f52',lw=1.2))

def setup(ax):
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_aspect('equal');ax.axis('off')

def niu_figure(number):
    fig=Figure(figsize=(10,5.8),dpi=110,layout='constrained')
    fig.get_layout_engine().set(rect=(0,.045,1,.955))
    f=next(x for x in FIGURES if x['number']==number)
    fig.suptitle('Fig. '+number+' · '+f['spanish'],fontsize=13,color='#183d50')
    if number=='3.1.3':
        a,b=fig.subplots(1,2);setup(a)
        path=np.array([[.1,.75],[.28,.78],[.42,.6],[.43,.35],[.6,.2],[.75,.3],[.9,.45]])
        a.plot(path[:,0],path[:,1],'--',color='#899ba7')
        for (x,y),label,ang in zip(path,['A','A\'','D','C','B','D\'','A\''],[0,-20,-60,-90,-30,20,0]):
            plane(a,x,y,.075,ang);arrow(a,(x,y),(x,y-.11),'W','#ba6b35',(-.04,-.035))
            sign=0 if label=='C' else (-1 if label in ['D',"D'"] else 1)
            nx,ny=-np.sin(np.radians(ang)),np.cos(np.radians(ang))
            if sign:arrow(a,(x,y),(x+sign*.15*nx,y+sign*.15*ny),'L',offset=(0,.015))
            else:a.text(x+.03,y+.08,'L = 0',fontsize=8,color='#226e91')
            a.annotate(label,(x,y),xytext=(-20,14),textcoords='offset points',fontsize=9)
        a.set_title('a) Posiciones y fuerzas cualitativas',fontsize=10)
        b.axhline(0,color='#405c6c');b.axvline(0,color='#405c6c')
        b.plot([-1,-.55,0,.65,1.3],[-.5,-.5,0,1,1],color='#226e91',lw=2)
        for x,y,l in [(-1,-.5,'D'),(-.55,-.5,"D'"),(0,0,'C'),(.33,.5,'B'),(.65,1,"A'"),(1.3,1,'A')]:
            b.scatter(x,y,color='#226e91');b.annotate(l,(x,y),xytext=(5,8),textcoords='offset points')
            b.plot([x,x],[0,y],':',color='#aebbc3',lw=.8)
        for x,y,t in [(.9,.4,'I'),(.3,.2,'II'),(-.25,-.1,'III'),(-.8,-.2,'IV')]:b.text(x,y,t,color='#6b818d')
        b.set(xlim=(-1.25,1.6),ylim=(-.8,1.35),xlabel='Coeficiente CL normalizado',ylabel='n / n máximo')
        b.set_title('b) Casos básicos de carga',fontsize=10);b.grid(alpha=.15)
    elif number=='3.3.1':
        a,b=fig.subplots(2,1);setup(a);setup(b);a.set_aspect('auto');b.set_aspect('auto')
        a.plot([.1,.45,.88],[.65,.32,.6],'--',color='#99acb7');b.plot([.1,.45,.88],[.4,.2,.4],'--',color='#99acb7')
        for i,(x,y,ang) in enumerate([(.16,.6,-30),(.48,.33,0),(.82,.6,20)]):
            plane(a,x,y,.12,ang);arrow(a,(x,y),(x,y+.25),'Lw');arrow(a,(x+.08,y),(x+.08,y+.13),'Lt')
            arrow(a,(x,y),(x,y-.22),'W','#b87936',(-.06,-.03));arrow(a,(x-.06,y),(x-.16,y+.04),'T','#517956')
            arrow(a,(x+.05,y),(x+.15,y+.02),'D','#a65555')
            if i==1:arrow(a,(x+.03,y-.05),(x+.03,y-.32),'Fi','#787586')
            xx=np.linspace(x-.1,x+.1,60);yy=(.25 if i==1 else .15)*np.sin(np.linspace(0,np.pi,60))
            b.plot(xx,.2+yy,color='#226e91');b.plot(xx,.2-yy*.6,color='#b97940');plane(b,x,.2,.12)
        a.set_title('a) Resultantes de fuerzas durante el cabeceo',fontsize=10);b.set_title('b) Presiones cualitativas asociadas',fontsize=10)
    elif number in ['3.3.2','3.3.3']:
        ax=fig.add_subplot();setup(ax);plane(ax,.47,.48,.4);cg=(.38,.48);ac=(.46,.49);tail=(.79,.5)
        ax.plot(*cg,'o',color='#243d4f');ax.text(.32,.39,'CG');ax.plot(*ac,'o',color='#637e8f');ax.text(.46,.4,'AC')
        arrow(ax,cg,(cg[0],.18),'nW' if number=='3.3.2' else 'W','#b47730',offset=(-.1,-.03))
        arrow(ax,ac,(ac[0],.85),'Lwb' if number=='3.3.2' else 'L de 1 g')
        arrow(ax,tail,(tail[0],.3),'Lt' if number=='3.3.2' else 'Cola de 1 g','#b47730')
        ax.annotate('',xy=(.79,.2),xytext=(.38,.2),arrowprops=dict(arrowstyle='<->',color='#677f8d'));ax.text(.58,.15,'lt')
        ax.annotate('',xy=(.46,.6),xytext=(.38,.6),arrowprops=dict(arrowstyle='<->',color='#677f8d'));ax.text(.4,.63,'xs')
        ax.add_patch(Arc((.38,.5),.23,.25,theta1=30,theta2=280,color='#406579'))
        if number=='3.3.2':
            ax.text(.18,.63,'Mwb');ax.text(.08,.03,'Equilibrio: Lt lt = Lwb xs + Mwb\nSignos según las flechas del esquema',fontsize=11)
        else:
            arrow(ax,(.79,.74),(.79,.53),'ΔT','#a44c4c');ax.text(.17,.65,'θ̈');ax.text(.08,.03,'Respuesta inicial: ΔT lt = Iyy θ̈\nEl incremento de cola genera aceleración angular',fontsize=11)
    elif number=='3.3.4':
        ax=fig.add_subplot();setup(ax);ax.set_aspect('auto')
        ax.add_patch(Ellipse((.5,.5),.1,.22,fc='#eaf0f4',ec='#224659'))
        ax.plot([.08,.92],[.5,.5],color='#224659',lw=5);arrow(ax,(.12,.5),(.12,.78),'+ΔFail')
        arrow(ax,(.88,.5),(.88,.22),'−ΔFail','#b57838',offset=(-.13,-.06))
        for x in [.12,.88]:ax.annotate('',xy=(x,.12),xytext=(.5,.12),arrowprops=dict(arrowstyle='<->',color='#7f929e'))
        ax.text(.3,.075,'y');ax.text(.7,.075,'y');ax.plot([.5,.5],[.15,.8],'--',color='#7f929e')
        ax.add_patch(Arc((.5,.65),.2,.25,theta1=30,theta2=160,color='#226e91'));ax.text(.59,.77,'ṗ')
        ax.text(.18,.94,'Par de alerones: 2 ΔFail y = Ixx ṗ',fontsize=12);ax.text(.33,.01,'Incremento local: Δn(y1) = ṗ y1 / g',fontsize=11)
    elif number in ['3.4.8','3.4.9','3.4.16']:
        ax=fig.add_subplot();v=np.linspace(0,1,501);sp=8*v*v;sm=-5*v*v
        top=np.minimum(sp,3);bot=np.maximum(sm,np.where(v<.8,-1.5,-1.5+(v-.8)*7.5))
        ax.axhline(0,color='#597482',lw=.8);ax.set(xlim=(0,1.12),ylim=(-3.6,5.8),xlabel='Velocidad normalizada',ylabel='Factor de carga esquemático')
        if number=='3.4.8':
            ax.plot(v,sp,color='#226e91');ax.plot(v,sm,color='#226e91')
            ax.hlines([3,4.5,-1.5,-2.25],0,1,colors=['#bd7d30','#a34545','#bd7d30','#a34545'],linestyles=['-','--','-','--'])
            ax.axvline(1,color='#3a5364');ax.text(.4,3.15,'Carga límite');ax.text(.5,4.65,'Carga última')
            ax.fill_between(v,3,4.5,where=v>.62,color='#e6bb78',alpha=.25);ax.fill_between(v,4.5,5.8,where=v>.75,color='#c87272',alpha=.15)
            ax.text(.77,3.75,'Posible daño',fontsize=9);ax.text(.8,5.3,'Falla',fontsize=9)
            ax.text(.08,1.6,'Capacidad positiva',fontsize=9);ax.text(.12,-2.7,'Capacidad negativa',fontsize=9)
        else:
            ax.plot(v,top,color='#226e91',lw=2,label='Maniobra');ax.plot(v,bot,color='#226e91',lw=2);ax.plot([1,1],[0,3],color='#226e91',lw=2)
            ax.plot(v,sp,':',color='#7d99ab');ax.plot(v,sm,':',color='#7d99ab')
            for x,label in [(.354,'Vs'),(.612,'VA'),(.8,'VC'),(1,'VD')]:ax.axvline(x,color='#b0bfc8',ls=':',lw=.7);ax.text(x,-.35,label,fontsize=9,ha='right' if label=='VD' else 'center')
            for x,y,label in [(.612,3,'PHA'),(.8,3,'PIA'),(1,3,'PLA'),(.548,-1.5,'NHA'),(.8,-1.5,'NIA'),(1,0,'NLA')]:ax.text(x,y+.14,label,fontsize=8)
            if number=='3.4.9':
                vf=np.linspace(0,.54,80);ax.plot(vf,np.minimum(12*vf*vf,2),'--',color='#b17936',label='Flaps extendidos')
                ax.text(.62,5.05,r'$V_e=V_{\mathrm{TAS}}\sqrt{\rho/\rho_0}$',fontsize=11,ha='center')
            else:
                upper=np.interp(v,[0,.5,.8,1],[1,3.8,4.2,2.8]);lower=2-upper
                ax.plot(v,upper,'--',color='#bd7e31',label='Ráfaga');ax.plot(v,lower,'--',color='#bd7e31')
                cp=np.minimum(sp,np.maximum(top,upper));cm=np.maximum(sm,np.minimum(bot,lower))
                ax.fill_between(v,cm,cp,color='#158578',alpha=.15,label='Extremos combinados')
                ax.plot([0,.8],[1,4.2],':',color='#bd7e31');ax.plot([0,1],[1,2.8],':',color='#bd7e31')
                ax.text(.48,4.7,'VB · +α, −M');ax.text(.75,-3,'−α, +M');ax.text(1.01,1.5,'CL = 0\n−M',fontsize=8)
            ax.legend(loc='upper left',fontsize=8)
        ax.grid(alpha=.18)
    elif number=='3.4.11':
        axes=fig.subplots(1,3)
        # Nomogramas de productos: escalas exteriores log(x), log(y), central log(xy)/2.
        # Líneas rectas de izquierda a derecha cruzan la escala central en el producto.
        a=5.25;ws=78.5;u=66;ve=180;kg=.75;R=a/ws;P=u*ve;dn=kg*P*R/498
        panels=[('a','R = a / (W/S)','1 / (W/S)',a,1/ws,[(2,8),(.015,.25),(.005,.05)]),
                ('Ude','P = Ude Ve','Ve',u,ve,[(10,100),(500,50000),(50,1000)]),
                ('R','Q = R P','P',R,P,[(.01,.2),(20,3000),(500,50000)])]
        for ax,(l,c,rr,x,y,ranges) in zip(axes,panels):
            ax.axis('off');ax.set(xlim=(-.2,2.3),ylim=(-.1,1.15))
            # Transformación exacta común de logaritmos con offsets independientes.
            lx0,lx1=np.log10(ranges[0]);ly0,ly1=np.log10(ranges[2]);span=max(lx1-lx0,ly1-ly0)
            for pos,label,low,high,shift,scale in [(0,l,*ranges[0],lx0,span),(2,rr,*ranges[2],ly0,span),(1,c,ranges[0][0]*ranges[2][0],ranges[0][1]*ranges[2][1],lx0+ly0,2*span)]:
                ax.plot([pos,pos],[0,1],color='#335a70')
                for val in np.geomspace(low,high,6):
                    yy=(np.log10(val)-shift)/scale;ax.plot([pos-.04,pos+.04],[yy,yy],color='#335a70');ax.text(pos+.06,yy,f'{val:.3g}',fontsize=7)
                ax.text(pos,1.06,label,ha='center',fontsize=8)
            yy1=(np.log10(x)-lx0)/span;yy2=(np.log10(y)-ly0)/span
            ax.plot([0,2],[yy1,yy2],color='#b57532',lw=2);ax.scatter([0,1,2],[yy1,(yy1+yy2)/2,yy2],s=18,color='#b57532')
        fig.text(.5,.03,f'Ejemplo propio: a={a:g}/rad, W/S={ws:g} lbf/ft², Ude={u:g} ft/s, Ve={ve:g} kt, Kg={kg:g}\nΔn = Kg Q / 498 = {dn:.4f}  →  n+ = {1+dn:.4f}; n− = {1-dn:.4f}',ha='center',fontsize=10)
        fig.set_layout_engine(None)
        for i,ax in enumerate(axes):ax.set_position([.035+i*.325,.25,.29,.58])
    elif number=='3.5.6':
        ax=fig.add_subplot();setup(ax);ax.set_aspect('auto')
        ax.add_patch(Ellipse((.5,.5),.9,.3,fill=False,edgecolor='#9bafb9',ls='--'))
        ax.add_patch(Rectangle((.27,.38),.47,.24,fc='#eaf1f4',ec='#244c62',lw=2))
        for x in [.33,.4,.47,.54,.61,.68]:
            ax.plot([x,x],[.38,.42],color='#335c71');ax.plot([x,x],[.58,.62],color='#335c71')
        labels=[(.27,.62,.02,.86,'Superior delantera\nCompresión +HAA\nTensión −LAA'),
                (.74,.62,.66,.86,'Superior trasera\nCompresión +LAA\nTensión −HAA'),
                (.27,.38,.02,.04,'Inferior delantera\nTensión +LAA\nCompresión −HAA'),
                (.74,.38,.66,.04,'Inferior trasera\nTensión +HAA\nCompresión −LAA')]
        for x,y,tx,ty,text in labels:
            ax.plot(x,y,'o',color='#b27732');ax.annotate(text,(x,y),xytext=(tx,ty),textcoords='data',fontsize=9,arrowprops=dict(arrowstyle='-',color='#7a909b'))
        ax.text(.04,.67,'Borde de ataque',fontsize=8);ax.text(.77,.33,'Borde de salida',fontsize=8)
        for x,y,ang,label in [(.18,.79,18,'+HAA'),(.82,.79,4,'+LAA'),(.18,.22,-18,'−HAA'),(.82,.22,-4,'−LAA')]:
            pts=np.array([[-.1,0],[0,.025],[.1,0],[0,-.008]])
            t=np.radians(-ang);R=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
            ax.add_patch(Polygon(pts@R.T+[x,y],fill=False,ec='#46748a'));ax.text(x,y-.055,label,ha='center',fontsize=8)
    fig.text(.99,.003,f'Redibujo interpretativo · Niu · impresa {f["page"]} / visor {f["viewer"]} · Sin escala',ha='right',fontsize=8,color='#667b88')
    return fig

def export_niu(directory):
    paths={}
    for f in FIGURES:
        fig=niu_figure(f['number']);name='niu_'+f['number'].replace('.','_')
        for ext in ['png','svg']:
            path=directory/(name+'.'+ext);fig.savefig(path,dpi=230,bbox_inches='tight');paths[(f['number'],ext)]=path
    return paths
