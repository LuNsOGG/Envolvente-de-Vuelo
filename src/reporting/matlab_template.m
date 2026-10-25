% Motor de calculo editable. Todas las velocidades de entrada son kt EAS.
% Fuentes: Niu cap. 3; Ap. A FAR 23 (2016) para el procedimiento separado.
show_figures = usejava('desktop');
resultados = struct([]);
base = fullfile(fileparts(mfilename('fullpath')), 'resultados_matlab');
outdir = base; attempt = 2;
while exist(outdir,'dir')
    outdir = [base '_' num2str(attempt)]; attempt = attempt + 1;
end
mkdir(outdir);
for idx = 1:numel(casos)
    cfg = casos(idx);
    assert(~isempty(regexp(cfg.id,'^[a-z0-9][a-z0-9_-]{0,63}$','once')),'Identificador de archivo invalido');
    r = calcular_niu(cfg);
    verificar_referencia(cfg,r);
    resultados(idx).case_id = cfg.id;
    resultados(idx).values = r.values;
    resultados(idx).curves = r.curves;
    escribir_json(fullfile(outdir,[cfg.id '_resultados.json']), r);
    escribir_curvas(fullfile(outdir,[cfg.id '_curvas.csv']),r.curves);
    dibujar(r.curves,cfg.name,fullfile(outdir,cfg.id),show_figures);
    if cfg.appendix_enabled
        ap = calcular_apendice(cfg);
        resultados(idx).appendix = ap;
        escribir_json(fullfile(outdir,[cfg.id '_apendice.json']),ap);
        escribir_curvas(fullfile(outdir,[cfg.id '_apendice_curvas.csv']),ap.curves);
        dibujar(ap.curves,[cfg.name ' - A4 academico'],fullfile(outdir,[cfg.id '_apendice']),show_figures);
    end
end
escribir_json(fullfile(outdir,'resumen.json'),resultados);
fprintf('OUTPUT_DIR=%s\n',outdir);

function r = calcular_niu(c)
    c=preparar(c);ws=c.W/c.S;
    assert(all(isfinite([c.W c.S c.N c.cp c.cn c.Vc c.Vd c.chord c.rho c.a c.g c.Ub c.Uc c.Ud])),'Entradas no finitas');
    assert(min([c.W c.S c.cp c.Vc c.Vd c.chord c.rho c.a c.g])>0 && c.N>=1 && c.nn<0 && c.cn<0 && min([c.Ub c.Uc c.Ud])>=0 && c.Vc<c.Vd,'Entradas fisicas incompatibles');
    assert(~strcmp(c.aero_model,'niu_table') || (strcmp(c.basis,'CL') && c.Cse>0 && c.Vd/c.Cse<=400/548.6+1e-9),'Tabla Mach fuera del intervalo o base incompatible');
    if strcmp(c.q_convention,'niu_296'),qf=1/296;else,qf=.5*c.rho0*c.kt_to_fps^2;end
    sp=@(x) qf.*x.^2.*c.cp.*escala(x,c)./ws;
    sn=@(x) qf.*x.^2.*c.cn.*escala(x,c)./ws;
    vs=primera_raiz(@(x)sp(x)-1,c.Vd);a=primera_raiz(@(x)sp(x)-c.N,c.Vd);g=primera_raiz(@(x)sn(x)-c.nn,c.Vd);
    assert(a<=c.Vc && g<=c.Vc,'A y G deben quedar antes de Vc');
    dc=delta(c.Vc,c.Uc,c);dd=delta(c.Vd,c.Ud,c);vb=NaN;
    av=[c.Vc c.Vd];ad=[dc dd];
    if c.Ub>0
        assert(c.Ub>=c.Uc,'Ub debe ser al menos Uc');
        vb=primera_raiz(@(x)sp(x)-1-delta(x,c.Ub,c),c.Vc);
        assert(vb<c.Vc,'Se requiere VB < Vc');av=[vb av];ad=[delta(vb,c.Ub,c) ad];
    end
    gd=@(x) rafaga(x,c,av,ad);
    gp=@(x)1+gd(x);gm=@(x)1-gd(x);
    knots=[0 c.Vc c.Vd vs a g];if ~isnan(vb),knots=[knots vb];end
    if strcmp(c.aero_model,'niu_table')
        k=c.book_v/548.6*c.Cse;knots=[knots k(k<=c.Vd)];
    end
    knots=[knots raices(@(x)sp(x)-gp(x),c.Vd) raices(@(x)sn(x)-gm(x),c.Vd) raices(@(x)gp(x)-c.N,c.Vd) raices(@(x)gm(x)-limite_negativo(x,c),c.Vd)];
    v=unique(sort([linspace(0,c.Vd,601) knots]));
    mp=min(sp(v),c.N);mn=max(sn(v),limite_negativo(v,c));
    curves=struct('V',v,'stall_pos',sp(v),'stall_neg',sn(v),'man_pos',mp,'man_neg',mn,'gust_pos',gp(v),'gust_neg',gm(v),'combined_pos',min(sp(v),max(mp,gp(v))),'combined_neg',max(sn(v),min(mn,gm(v))));
    mu=2*ws/(c.rho*c.chord*pendiente(c.Vc,c)*c.g);kg=.88*mu/(5.3+mu);
    vals=struct('W',c.W,'S',c.S,'W_S',ws,'n_pos',c.N,'n_neg',c.nn,'CN_pos',c.cp,'CN_neg',c.cn,'Vc',c.Vc,'Vd',c.Vd,'Vs',vs,'V_A_stall',a,'V_G_stall',g,'Vb',vb,'mu',mu,'Kg',kg,'chord',c.chord,'n3',1+dc,'n4',1-dc,'n_gust_c_pos',1+dc,'n_gust_c_neg',1-dc,'n_gust_d_pos',1+dd,'n_gust_d_neg',1-dd,'Va_selected',c.Va_selected);
    r=struct('case_id',c.id,'name',c.name,'values',vals,'curves',curves);
end
function y=pendiente(x,c)
    if strcmp(c.aero_model,'niu_table'),y=c.a*interp1(c.book_v/548.6,c.book_a,x/c.Cse,'linear')/5.22;else,y=c.a+zeros(size(x));end
end
function y=escala(x,c)
    if strcmp(c.aero_model,'niu_table'),y=interp1(c.book_v/548.6,c.book_cl,x/c.Cse,'linear')/1.3;else,y=ones(size(x));end
end
function y=delta(x,u,c)
    aa=pendiente(x,c);mu=2*(c.W/c.S)./(c.rho*c.chord*aa*c.g);kg=.88*mu./(5.3+mu);
    y=kg.*u.*x.*aa/(498*(c.W/c.S));
end
function y=rafaga(x,c,av,ad)
    y=zeros(size(x));u=c.Uc;if c.Ub>0,u=c.Ub;end
    first=x<=av(1);y(first)=delta(x(first),u,c);
    y(~first)=interp1(av,ad,x(~first),'linear');
end
function y=limite_negativo(x,c)
    y=c.nn+zeros(size(x));
    if ~strcmp(c.negative_end,'constant')
        target=-1;if strcmp(c.negative_end,'zero'),target=0;end
        mask=x>c.Vc;y(mask)=c.nn+(target-c.nn)*(x(mask)-c.Vc)/(c.Vd-c.Vc);
    end
end
function xs=raices(fun,upper)
    xs=[];lo=0;flo=fun(lo);if abs(flo)<1e-12,xs=[xs lo];end
    for i=1:600
        hi=upper*i/600;fhi=fun(hi);
        if flo*fhi<0
            left=lo;right=hi;fl=flo;
            for j=1:55
                mid=(left+right)/2;fm=fun(mid);
                if fl*fm<=0,right=mid;else,left=mid;fl=fm;end
            end
            xs=[xs (left+right)/2]; %#ok<AGROW>
        elseif abs(fhi)<1e-12,xs=[xs hi]; %#ok<AGROW>
        end
        lo=hi;flo=fhi;
    end
    xs=unique(round(xs,11));
end
function x=primera_raiz(fun,upper)
    xs=raices(fun,upper);assert(~isempty(xs),'No existe interseccion en el intervalo');x=xs(1);
end
function c=preparar(c)
    if strcmp(c.chord_mode,'geometric'), c.chord=c.S/c.span; end
    ws=c.W/c.S;
    if strcmp(c.speed_mode,'excel')
        c.Vc=17*sqrt(max(c.N,3.8)*ws);c.Vd=24*sqrt(max(c.N,3.8)*ws);
    elseif strcmp(c.speed_mode,'subparte_c')
        k=33;kd=1.4;
        if strcmp(c.category,'utilidad'),kd=1.5;end
        if strcmp(c.category,'acrobática'),k=36;kd=1.55;end
        c.Vc=k*sqrt(ws);c.Vd=max(1.25*c.Vc,kd*c.Vc);
    end
    if strcmp(c.negative_rule,'excel'),c.nn=-.5*c.N;end
    if strcmp(c.negative_rule,'normal'),c.nn=-.4*c.N;end
    if strcmp(c.negative_rule,'transport'),c.nn=-1;end
end
function r=calcular_apendice(c)
    c=preparar(c);
    assert(strcmp(c.basis,'CN'),'El Apendice A requiere CN');ws=c.W/c.S;n2=-.5*c.N;
    base=sqrt(max(c.N,3.8)*ws);vc=c.Vc;vd=c.Vd;
    if strcmp(c.appendix_speed,'minimum'),vc=17*base;vd=24*base;end
    assert(isfinite(c.ap_n3) && isfinite(c.ap_n4) && c.ap_n3>0 && c.ap_n4<0 && ~isempty(strtrim(c.ap_source)),'Documente n3/n4 y su fuente antes de ejecutar A4');
    qf=.5*c.rho0*c.kt_to_fps^2;kp=qf*c.cp/ws;kn=qf*c.cn/ws;vs=sqrt(1/kp);a=sqrt(c.N/kp);g=sqrt(n2/kn);
    assert(a<vc && g<vc && vc<vd,'Secuencia de velocidades incompatible con A4');
    v=unique(sort([linspace(0,vd,601) 0 vc vd vs a g]));sp=kp*v.^2;sn=kn*v.^2;
    upper=sp;lower=sn;nc=max(c.N,c.ap_n3);nf=min(n2,c.ap_n4);
    mid=v>a & v<=vc;upper(mid)=c.N+(nc-c.N)*(v(mid)-a)/(vc-a);last=v>vc;upper(last)=nc+(c.N-nc)*(v(last)-vc)/(vd-vc);
    mid=v>g & v<=vc;lower(mid)=n2+(nf-n2)*(v(mid)-g)/(vc-g);lower(last)=nf+(n2-nf)*(v(last)-vc)/(vd-vc);
    curves=struct('V',v,'stall_pos',sp,'stall_neg',sn,'man_pos',min(sp,c.N),'man_neg',max(sn,n2),'combined_pos',upper,'combined_neg',lower);
    vals=struct('W_S',ws,'Vc_A_raw',17*base,'Vd_A_raw',24*base,'Va_A_raw',15*base,'Vf_A_raw',11*base,'Vc',vc,'Vd',vd,'Vs',vs,'V_A_stall',a,'V_G_stall',g,'n3',c.ap_n3,'n4',c.ap_n4,'n_pos',c.N,'n_neg',n2);
    r=struct('values',vals,'curves',curves,'source',c.ap_source,'notice','Procedimiento academico; revisar aplicabilidad, no equivale a certificacion.');
end
function escribir_json(path,value)
    fid=fopen(path,'w','n','UTF-8');assert(fid>=0,'No se puede escribir JSON');cleanup=onCleanup(@()fclose(fid));fprintf(fid,'%s',jsonencode(value));
end
function escribir_curvas(path,c)
    fields=fieldnames(c);data=zeros(numel(c.V),numel(fields));
    for j=1:numel(fields),data(:,j)=c.(fields{j})(:);end
    fid=fopen(path,'w','n','UTF-8');assert(fid>=0,'No se puede escribir CSV');cleanup=onCleanup(@()fclose(fid));fprintf(fid,'%s\n',strjoin(fields,','));
    fmt=[repmat('%.17g,',1,numel(fields)-1) '%.17g\n'];fprintf(fid,fmt,data');
end
function dibujar(c,name,prefix,show_figures)
    visible='off';if show_figures,visible='on';end
    kinds={'man','gust','combined'};titles={'Maniobras','Rafagas','Combinado'};
    for j=1:numel(kinds)
        key=kinds{j};if ~isfield(c,[key '_pos']),continue;end
        f=figure('Visible',visible,'Color','w','Name',[name ' - ' titles{j}]);ax=axes('Parent',f);hold(ax,'on');grid(ax,'on');
        if strcmp(key,'combined') && isfield(c,'gust_pos')
            plot(ax,c.V,c.gust_pos,'-.','Color',[.5 .5 .5]);plot(ax,c.V,c.gust_neg,'-.','Color',[.5 .5 .5]);
        end
        plot(ax,c.V,c.([key '_pos']),'k','LineWidth',1.8);plot(ax,c.V,c.([key '_neg']),'k','LineWidth',1.8);
        plot(ax,[c.V(end) c.V(end)],[c.([key '_pos'])(end) c.([key '_neg'])(end)],'k');
        xlabel(ax,'V [kt EAS]');ylabel(ax,'n [1]');title(ax,[name ' - ' titles{j}],'Interpreter','none');
        print(f,[prefix '_' key '.png'],'-dpng','-r150');if ~show_figures,close(f);end
    end
end

function verificar_referencia(c,r)
    signature=[c.W c.S c.N c.nn c.cp c.cn c.Vc c.Vd c.rho c.chord c.span c.a c.g c.Ub c.Uc c.Ud c.Cse c.Va_selected c.rho0 c.kt_to_fps c.ap_n3 c.ap_n4 double(c.appendix_enabled) c.book_v c.book_a c.book_cl];
    modes={c.basis c.category c.speed_mode c.negative_rule c.negative_end c.aero_model c.chord_mode c.q_convention c.appendix_speed};
    if isequaln(signature,c.reference_signature) && isequal(modes,c.reference_modes)
        for k=1:numel(c.reference_keys)
            key=c.reference_keys{k};expected=c.reference_values(k);actual=r.values.(key);
            assert(abs(actual-expected)<=max(1e-8,abs(expected)*1e-9),['Resultado distinto de la referencia: ' key]);
        end
        fprintf('REFERENCE_OK=%s\n',c.id);
    else
        fprintf('Entradas modificadas; referencia inicial omitida: %s\n',c.id);
    end
end
