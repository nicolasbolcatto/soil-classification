#Field and laboratory data import
import pandas as pd
perforacion_df = pd.read_csv('/datos_perf.csv')
perforacion_df.head()

#SPT calculation
#The number of blows required to penetrate the las 30 cm. is computed. If record show more than 50 blows for this penetration
#without reaching 30 cm., extrapolation is performed.

penetracion_SPT=perforacion_df['d2']+perforacion_df['d3']
NSPT=list(perforacion_df['n2']+perforacion_df['n3']*30/penetracion_SPT)

#Natural water content

#Se crea un objeto lista que contiene los números de pesafiltro como keys y sus pesos (tara) como values

pesafiltros_df = pd.read_csv('pesafiltros_campo.csv')
pesafiltros_campo = list(pesafiltros_df['pesafiltro'])
pesos_campo = list(pesafiltros_df['peso'])

#Se crea una lista que reune los pesafiltros utilizados en la perforacion y se crea una lista que contiene los
#pesos de los mismos

utilizados=list(perforacion_df['w_pesafiltro'])
pesos_pf_campo=[]
for i in utilizados:
    posicion = pesafiltros_campo.index(i)
    pesos_pf_campo.append(pesos_campo[posicion])

#Se define la función que calcula la humedad a partir del peso humedo, el peso seco y el peso del pesafiltro

def contenido_humedad(msh,mss,pesafiltros):
    agua = msh - mss
    suelo_seco = mss - pesafiltros
    humedad = round(100*agua/suelo_seco,1)
    return(humedad)

#Se invoca la función con las listas que representan las masas de suelo húmedo, seco y los pesos de pesafiltros
#y calcula la humedad, guardandola en una lista "w"

w_mh=list(perforacion_df['w_msh'])
w_ms=list(perforacion_df['w_mss'])
i=0
w=[]
while i < len(w_mh):
    w.append(contenido_humedad(w_mh[i],w_ms[i],pesos_pf_campo[i]))
    i +=1

#Cálculo de los límites de Atterberg
#Limite liquido
import math
LL_pf1=list(perforacion_df['LL_pesafiltro1'])
LL_pf2=list(perforacion_df['LL_pesafiltro2'])
LL_msh1=list(perforacion_df['LL_msh1'])
LL_msh2=list(perforacion_df['LL_msh2'])
LL_mss1=list(perforacion_df['LL_mss1'])
LL_mss2=list(perforacion_df['LL_mss2'])
LL_N1=list(perforacion_df['LL_N1'])
LL_N2=list(perforacion_df['LL_N2'])

pesafiltros_df = pd.read_csv('pesafiltros_laboratorio.csv')
pesafiltros_lab = list(pesafiltros_df['pesafiltro'])
pesos_lab = list(pesafiltros_df['peso'])

LL_pesos_pf_lab_1=[]
for i in LL_pf1:
    posicion = pesafiltros_lab.index(i)
    LL_pesos_pf_lab_1.append(pesos_lab[posicion])

LL_pesos_pf_lab_2=[]
for i in LL_pf2:
    if math.isnan(LL_pf2[LL_pf2.index(i)]):
        LL_pesos_pf_lab_2.append(0)
    else:
        posicion = pesafiltros_lab.index(i)
        LL_pesos_pf_lab_2.append(pesos_lab[posicion])

#Se define la función que calcula el límite líquido, ya sea como interpolacion de dos muestras en el caso de que
#se hayan ejecutado o como extrapolación de una muestra, si solo se ha ejecutado una.
def LL(N1,msh1,mss1,pf1,N2,msh2,mss2,pf2):
    if math.isnan(N2):
        w=100*(msh1-mss1)/(mss1-pf1)
        LL=w/(1.419-0.3*(math.log(N1,10)))
        return LL
    else:
        w1=(msh1-mss1)/(mss1-pf1)
        w2=(msh2-mss2)/(mss2-pf2)
        LL=w1+(N1-25)*((w2-w1)/(N1-N2))
        return LL
        
#Se invoca la función sobre los datos de la tabla de entrada
i=0
limite_liquido = []
while i < len(LL_N1):
    limite_liquido.append(LL(LL_N1[i],LL_msh1[i],LL_mss1[i],LL_pesos_pf_lab_1[i],LL_N2[i],LL_msh2[i],LL_mss2[i],LL_pesos_pf_lab_2[i]))
    i += 1

#Limite plástico

LP_pf1=list(perforacion_df['LP_pesafiltro1'])
LP_pf2=list(perforacion_df['LP_pesafiltro2'])
LP_msh1=list(perforacion_df['LP_msh1'])
LP_msh2=list(perforacion_df['LP_msh2'])
LP_mss1=list(perforacion_df['LP_mss1'])
LP_mss2=list(perforacion_df['LP_mss2'])

LP_pesos_pf_lab_1=[]
for i in LP_pf1:
    posicion = pesafiltros_lab.index(i)
    LP_pesos_pf_lab_1.append(pesos_lab[posicion])

LP_pesos_pf_lab_2=[]
for i in LP_pf2:
    posicion = pesafiltros_lab.index(i)
    LP_pesos_pf_lab_2.append(pesos_lab[posicion])

i=0
limite_plastico = []
while i < len(LP_msh1):
    wp1=100*(LP_msh1[i]-LP_mss1[i])/(LP_mss1[i]-LP_pesos_pf_lab_1[i])
    wp2=100*(LP_msh2[i]-LP_mss2[i])/(LP_mss2[i]-LP_pesos_pf_lab_2[i])
    wp=0.5*(wp1+wp2)
    limite_plastico.append(wp)
    i += 1

#Indice plástico
i=0
indice_plastico=[]
while i < len(limite_liquido):
    indice_plastico.append(limite_liquido[i]-limite_plastico[i])
    i+=1

#Clasificacion SUCS
#Se declara la funcion para clasificar al suelo mediante el Sistema Unificado de Clasificacion de suelos, a partir de los límites de Atterberg
#y los resultados del análisis granulométrico

def SUCS(LL,LP,IP,p4,p10,p40,p200,CU,CC):
        CF = 100 - p200 #fraccion gruesa
        F1 = p4 - p200  #material que pasa el tamiz #4 y queda retenido en el tamiz #200
        GF = 100 - p4   #grava
        SF = p4 - p200  #arena
        
        if p200 < 50:                                       #suelo de grano grueso
            if F1 <= CF*0.5:                                    #grava
                if p200 < 5:
                    if CU >= 4 and CC >=1 and CC <= 3:
                        SUCS = "GW"
                        Descripcion = "Grava bien graduada"
                    else:
                        SUCS = "GP"
                        Descripcion = "Grava mal graduada"
                elif 5 <= p200 <= 12:
                    if CU >= 4 and CC >=1 and CC <= 3:
                        if IP < 4 or IP < 0.73*(LL-20):
                            SUCS = "GW-GM"
                            if SF < 15:
                                Descripcion = "Grava bien graduada con limo"
                            else:
                                Descripcion = "Grava bien graduada con limo y arena"
                        elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                            SUCS = "GW-GC"
                            if SF < 15:
                                Descripcion = "Well-graded gravel with silty clay"
                            else:
                                Descripcion = "Well-graded gravel with silty clay and sand"
                        else:
                            SUCS = "GW-GC"
                            if SF < 15:
                                Descripcion = "Grava bien graduada con arcilla"
                            else:
                                Descripcion = "Grava bien graduada con arcilla y arena"
                    else:
                        if IP < 4 or IP < 0.73*(LL-20):
                            SUCS = "GP-GM"
                            if SF < 15:
                                Descripcion = "Grava mal graduada con limo"
                            else:
                                Descripcion = "Grava mal graduada con limo y arena"
                        elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                            SUCS = "GP-GC"
                            if SF < 15:
                                Descripcion = "Grava mal graduada con arcilla limosa"
                            else:
                                Descripcion = "Grava mal graduada con arcilla limosa y arena"
                        else:
                            SUCS = "GP-GC"
                            if SF < 15:
                                Descripcion = "Grava mal graduada con arcilla"
                            else:
                                Descripcion = "Grava mal graduada con arcilla y arena"   
                else:
                    if IP < 4 or IP < 0.73*(LL-20):
                        SUCS = "GM"
                        if SF < 15:
                            Descripcion = "Grava limosa"
                        else:
                            Descripcion = "Grava limosa con arena"
                    elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                        SUCS = "GC-GM"
                        if SF < 15:
                            Descripcion = "Grava limo-arcillosa"
                        else:
                            Descripcion = "Grava limo-arcillosa con arena"
                    else:
                        SUCS = "GC"
                        if SF < 15:
                            Descripcion = "Grava arcillosa"
                        else:
                            Descripcion = "Grava arcillosa con arena" 
            else:                                               #Arena
                if p200 < 5:
                    if CU >= 6 and CC >=1 and CC <= 3:
                        SUCS = "SW"
                        Descripcion = "Arena bien graduada"
                    else:
                        SUCS = "SP"
                        Descripcion = "Arena mal graduada"
                elif 5 <= p200 <= 12:
                    if CU >= 6 and CC >=1 and CC <= 3:
                        if IP < 4 or IP < 0.73*(LL-20):
                            SUCS = "SW-SM"
                            if GF < 15:
                                Descripcion = "Arena bien graduada con limo"
                            else:
                                Descripcion = "Arena bien graduada con limo y grava"
                        elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                            SUCS = "SW-SC"
                            if GF < 15:
                                Descripcion = "Arena bien graduada con arcilla limosa"
                            else:
                                Descripcion = "Arena bien graduada con arcilla limosa y grava"
                        else:
                            SUCS = "SW-SC"
                            if GF < 15:
                                Descripcion = "Arena bien graduada con arcilla"
                            else:
                                Descripcion = "Arena bien graduada con arcilla grava"
                    else:
                        if IP < 4 or IP < 0.73*(LL-20):
                            SUCS = "SP-SM"
                            if GF < 15:
                                Descripcion = "Arena mal graduada con limo"
                            else:
                                Descripcion = "Arena mal graduada con limo y grava"
                        elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                            SUCS = "SP-SC"
                            if GF < 15:
                                Descripcion = "Arena mal graduada con arcilla limosa"
                            else:
                                Descripcion = "Arena mal graduada con arcilla limosa y grava"
                        else:
                            SUCS = "SP-SC"
                            if GF < 15:
                                Descripcion = "Arena mal graduada con arcilla"
                            else:
                                Descripcion = "Arena mal graduada con arcilla y grava"
                else:
                    if IP < 4 or IP < 0.73*(LL-20):
                        SUCS = "SM"
                        if GF < 15:
                            Descripcion = "Arena limosa"
                        else:
                            Descripcion = "Arena limosa con grava"
                    elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):
                        SUCS = "SC-SM"
                        if GF < 15:
                            Descripcion = "Arena limo-arcillosa"
                        else:
                            Descripcion = "Arena limo-arcillosa con grava"
                    else:
                        SUCS = "SC"
                        if GF < 15:
                            Descripcion = "Arena arcillosa"
                        else:
                            Descripcion = "Arena arcillosa con grava"
        else:                                               #Suelo de grano fino
            if LL < 50:                                         #Baja plasticidad
                if IP < 4 or IP < 0.73*(LL-20):                     
                    SUCS = "ML"
                    if CF < 30:
                        if CF < 15:
                            Descripcion = "Limo"
                        elif GF > SF:
                            Descripcion = "Limo con grava"
                        else:
                            Descripcion = "Limo con arena"
                    elif GF > SF:
                        if SF < 15:
                            Descripcion = "Limo gravoso"
                        else:
                            Descripcion = "Limo gravoso con arena"
                    else:
                        if GF < 15:
                            Descripcion = "Limo arenoso"
                        else:
                            Descripcion = "Limo arenoso con grava"
                elif 4 <= IP <= 7 and IP >= 0.73*(LL-20):           
                     SUCS = "CL-ML"
                     if CF < 30:
                        if CF < 15:
                             Descripcion = "Arcilla limosa"
                        elif GF > SF:
                            Descripcion = "Arcilla limosa con grava"
                        else:
                            Descripcion = "Arcilla limosa con arena"
                     elif GF > SF:
                        if SF < 15:
                            Descripcion = "Arcilla limo-gravosa"
                        else:
                            Descripcion = "Arcilla limo-gravosa con arena"
                     else:
                        if GF < 15:
                            Descripcion = "Arcila limo-arenosa"
                        else:
                            Descripcion = "Arcila limo-arenosa con grava"
                else:                                               
                     SUCS = "CL"
                     if CF < 30:
                        if CF < 15:
                            Descripcion = "Arcilla de baja plasticidad"
                        elif GF > SF:
                            Descripcion = "Arcilla de baja plasticidad con grava"
                        else:
                            Descripcion = "Arcilla de baja plasticidad con arena"
                     elif GF > SF:
                        if SF < 15:
                            Descripcion = "Arcilla gravosa de baja plasticidad"
                        else:
                            Descripcion = "Arcilla de baja plasticidad con arena"
                     else:
                        if GF < 15:
                            Descripcion = "Arcilla arenosa de baja plasticidad"
                        else:
                            Descripcion = "Arcilla arenosa de baja plasticidad con grava"
            else:                                               
                if IP < 0.73*(LL-20):                               
                    SUCS = "MH"
                    if CF < 30:
                        if CF < 15:
                            Descripcion = "Limo arcilloso de alta plasticidad"
                        elif GF > SF:
                            Descripcion = "Limo arcilloso de alta plasticidad con grava"
                        else:
                            Descripcion = "Limo arcilloso de alta plasticidad con arena"
                    elif GF > SF:
                        if SF < 15:
                            Descripcion = "Limo-arcillo gravoso de alta plasticidad"
                        else:
                            Descripcion = "Limo-arcillo gravoso de alta plasticidad con arena"
                    else:
                        if GF < 15:
                            Descripcion = "Limo arcillo-arenoso de alta plasticidad"
                        else:
                            Descripcion = "Limo arcillo-arenoso de alta plasticidad con grava"
                else:                                                
                     SUCS = "CH"
                     if CF < 30:
                        if CF < 15:
                             Descripcion = "Arcilla de alta plasticidad"
                        elif GF > SF:
                            Descripcion = "Arcilla gravosa de alta plasticidad"
                        else:
                            Descripcion = "Arcilla gravosa de alta plasticidad con arena"
                     elif GF > SF:
                         if SF < 15:
                             Descripcion = "Arcilla de alta plasticidad con grava"
                         else:
                             Descripcion = "Arcilla de alta plasticidad con grava y arena"
                     else:
                        if GF < 15:
                            Descripcion = "Arcilla arenosa de alta plasticidad"
                        else:
                            Descripcion = "Arcilla arenosa de alta plasticidad con arena"
        return(SUCS,Descripcion)

#Se invoca la función para crear una lista de resultados
gran_4=list(perforacion_df['gran_4'])
gran_10=list(perforacion_df['gran_10'])
gran_40=list(perforacion_df['gran_40'])
gran_200=list(perforacion_df['gran_200'])
CU=list(perforacion_df['CU'])
CC=list(perforacion_df['CC'])

i=0
Clasificacion = []
while i < len(gran_4):
    Clasificacion.append(SUCS(limite_liquido[i],limite_plastico[i],indice_plastico[i],gran_4[i],gran_10[i],gran_40[i],gran_200[i],CU[i],CC[i]))
    i += 1

#Se grafican los resultados en 3 gráficas (una para el SPT, otra para la humedad natural y los límites de Atterberg
#y la tercera para la granulometría)
import matplotlib.pyplot as plt

fig, axes = plt.subplots(nrows=1, ncols=3)
profundidad=list(perforacion_df['prof_med'])

axes[0].plot(NSPT,profundidad, 'b')
axes[0].set_xlabel('NSPT')
axes[0].set_ylabel('Profundidad (m.)')
axes[0].set_title('NSPT')
axes[0].invert_yaxis()
axes[0].set_xticks(range(0, 60, 10))

axes[1].plot(w,profundidad, 'r',label="wnat")
axes[1].plot(limite_liquido,profundidad, 'g--',label="LL")
axes[1].plot(limite_plastico,profundidad, 'b--',label="LP")
axes[1].set_xlabel('Humedad (%)')
axes[1].set_ylabel('Profundidad (m.)')
axes[1].set_title('Humedad, LL y LP')
axes[1].invert_yaxis()
axes[1].set_xticks(range(0, 90, 20))
axes[1].legend()

axes[2].plot(gran_10,profundidad, 'r',label="#10")
axes[2].plot(gran_40,profundidad, 'g',label="#40")
axes[2].plot(gran_200,profundidad, 'b',label="#200")
axes[2].set_xlabel('% que pasa')
axes[2].set_ylabel('Profundidad (m.)')
axes[2].set_title('Granulometría')
axes[2].invert_yaxis()
axes[2].set_xticks(range(0, 110, 20))
axes[2].legend()

fig.tight_layout()