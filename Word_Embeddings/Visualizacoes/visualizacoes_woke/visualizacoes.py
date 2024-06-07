import matplotlib.pyplot as plt
import numpy as np
from .funcoes import limparConsole, obterResposta
from gensim.models import KeyedVectors
import time
import os
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import pandas as pd
import re
import string
try:
  # try: # Se tiver rodando no Colab já será instalado o spaCy e o modelo treinado em português para reconhecer os verbos no filtro, se não (execução local) terá que ser instalado "manualmente" com estes comandos no terminal sem o "!" na frente.
  #   !pip install -U spacy
  #   !pip install -U spacy-lookups-data
  #   !python -m spacy download pt_core_news_lg
  # except Exception:
  #   pass
  import spacy
  nlp = spacy.load('pt_core_news_lg',enable=["tok2vec","morphologizer"])
except Exception:
  print('\n\n\t! spaCy não foi importado com sucesso, o filtro de verbos não poderá ser utilizado.\n\n')
  time.sleep(3)


PONTUACOES = string.punctuation

PASTA_SAVE_IMAGENS = r'imagens_geradas'



def verificaExistenciaNosModelos(modelos_treinados : list[tuple], palavra_central : str):
  try:
    for modelo in [modelo[1] for modelo in modelos_treinados]:
      modelo[palavra_central]
    return True
  except Exception:
    return False

def SimilaridadesAoDecorrerDoTempo(modelos_treinados : list[tuple],pasta_para_salvar=PASTA_SAVE_IMAGENS):
  
  print('\n\n\tVocê está montando uma visualização para Vizinhos mais próximos ao decorrer do tempo.\n\n')
  palavra_central = input('Digite a palavra central: ').lower().strip()
  
  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra_central):
    palavra_central = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra palavra: ').lower().strip()
    
  cores = ['green','red','cyan','violet','blue','gold','orange','c','black','purple','lime','tomato','magenta','lightslategrey','lightgreen','paleturquoise','aquamarine','moccasin','lightcoral','chocolate','sandybrown','rosybrown']


  lista_palavras_comparacao = []
  while True:

    if len(lista_palavras_comparacao) < len(cores):
      palavra_digitada = input(f'\nDigite uma palavra para ser comparada (no máximo {len(cores)} e 0 para parar):  ').lower().strip()

      if (palavra_digitada != '0') and verificaExistenciaNosModelos(modelos_treinados,palavra_digitada):
        lista_palavras_comparacao.append(palavra_digitada)
      elif (verificaExistenciaNosModelos(modelos_treinados,palavra_digitada) == False) and (palavra_digitada != '0'):
        while (verificaExistenciaNosModelos(modelos_treinados,palavra_digitada) == False) and (palavra_digitada != '0'):
          palavra_digitada = input(f'O token "{palavra_digitada}" não está presente em todos os modelos.\nPor favor, digite outro token:  ').lower().strip()
        if palavra_digitada != '0':
          lista_palavras_comparacao.append(palavra_digitada)
      else:
        break
    else:
      break



  nomes = [re.search(r'(\d{4})\_\d{4}',modelo[0]).group(1) + '\n-\n' + re.search(r'\d{4}\_(\d{4})',modelo[0]).group(1) for modelo in modelos_treinados]

  fig, ax = plt.subplots(figsize=(16, 8))

  x = [i+1 for i in range(len(modelos_treinados))]

  cores_usadas = []
  for palavra in lista_palavras_comparacao:
    i = 0
    cor = cores[i]
    while cor in cores_usadas:
      cor = cores[i+1]
      i += 1
    cores_usadas.append(cor)
    y = []
    for modelo in [modelo[1] for modelo in modelos_treinados]:
      y.append(modelo.similarity(palavra_central,palavra))

    ax.scatter(x, y, color='black', s=10)
    line_x = [x[0]] + x[1:-1] + [x[-1]]
    line_y = [y[0]] + y[1:-1] + [y[-1]]
    ax.plot(line_x, line_y, label=palavra, color=cor)
    for i in range(len((y))):
      ax.text(x[i], y[i]+0.01, str(round(y[i],2)), fontsize=6, ha='center', va='bottom')

  nome_modelo = re.sub(r'\_\d{4}\_\d{4}', '', modelos_treinados[0][0])

  ax.set_title(f'Similaridade entre "{palavra_central}" e outras palavras selecionadas\n{nome_modelo}', fontsize=20, pad= 25)
  ax.set_xlabel('Intervalos de tempo', fontsize=15, labelpad=20)
  ax.set_ylabel('Similaridade', fontsize=15, labelpad=20)

  ax.set_xticks(x)
  ax.set_xticklabels(nomes,fontsize=11)

  ax.grid('on')
  ax.legend(fontsize = 11,loc='center left', bbox_to_anchor=(1, 0.5))
  plt.tight_layout(rect=[0, 0, 0.85, 1])

  limparConsole()

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Gráfico Similaridades',palavra_central)

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)

  ano_inicial = re.search(r'(\d{4})\_\d{4}',modelos_treinados[0][0]).group(1)
  ano_final = re.search(r'\d{4}\_(\d{4})',modelos_treinados[-1][0]).group(1)

  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Similaridades para modelos de {ano_inicial} até {ano_final}.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  plt.clf()
  # plt.show()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Gráfico Similaridades','-->',palavra_central,'\n\n')
  

def VizinhosMaisProximosAoDecorrerDoTempo(modelos_treinados,pasta_para_salvar=PASTA_SAVE_IMAGENS):
  print('\n\n\tVocê está montando uma visualização para Vizinhos mais Próximos ao decorrer do tempo.\n\n')
  palavra_central = input('Digite uma palavra: ').lower().strip()
  
  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra_central):
    palavra_central = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra palavra: ').lower().strip()

  if not os.path.exists(pasta_para_salvar):
    os.makedirs(pasta_para_salvar)

  for modelo in modelos_treinados:
    VizinhosMaisProximos(tupla_modelo_escolhido=modelo,
                        palavra_central=palavra_central,
                        pasta_para_salvar=pasta_para_salvar)
        
def VizinhosMaisProximos(tupla_modelo_escolhido : tuple[str,KeyedVectors],
                        palavra_central : str,
                        pasta_para_salvar : str):
  
  try:
    nome_modelo_escolhido = tupla_modelo_escolhido[0]
    modelo_escolhido = tupla_modelo_escolhido[1]
    
    palavras_vizinhas = modelo_escolhido.most_similar(palavra_central)

    palavras_vizinhas = []
    palavras_vizinhas_com_similaridade= []

    for palavra in modelo_escolhido.most_similar(palavra_central):
      palavras_vizinhas.append(palavra[0])
      palavras_vizinhas_com_similaridade.append((palavra[0],palavra[1]))


    fig, ax = plt.subplots(1, 2,figsize=(12, 5),gridspec_kw={'width_ratios': [4, 1]})

    ax[0].axis('off')
    ax[1].axis('off')

    ax[0].text(0.5, 0.5, palavra_central, ha='center', va='center', fontsize=14, fontweight='bold')

    num_vizinhas = len(palavras_vizinhas)

    theta = np.linspace(0, 2 * np.pi, num_vizinhas, endpoint=False)
    raio = 0.1

    x_vizinhas = 0.5 + raio * np.cos(theta)
    y_vizinhas = 0.5 + raio * np.sin(theta)

    distancia_raio = 0.7

    for i, palavra in enumerate(palavras_vizinhas):
        ax[0].text(x_vizinhas[i], y_vizinhas[i], palavra, ha='center', va='center', fontsize=12, fontweight='bold')

        x_inicio = x_vizinhas[i] + (0.5 - x_vizinhas[i]) * distancia_raio
        y_inicio = y_vizinhas[i] + (0.5 - y_vizinhas[i]) * distancia_raio
        x_fim = x_vizinhas[i]
        y_fim = y_vizinhas[i]

        ax[0].plot([x_inicio, x_fim], [y_inicio, y_fim], color='gray')

    ax[0].set_title(f'TOP 10 Vizinhos mais próximos de {palavra_central}\n{nome_modelo_escolhido}')

    texto = "Resultado:\n('palavra', similaridade)"
    for i in range(len(palavras_vizinhas_com_similaridade)):
      texto += '\n\n'+str(palavras_vizinhas_com_similaridade[i])

    ax[1].text(1, 0.5,texto, fontsize=11, ha='center', va='center')

    
    pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Vizinhos mais próximos',palavra_central)

    if not os.path.exists(pasta_para_salvar_palavra_central):
      os.makedirs(pasta_para_salvar_palavra_central)
    
    caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Vizinhos mais próximos - {nome_modelo_escolhido} - {palavra_central}.png')

    while os.path.exists(caminho_save_fig):  
      caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

    plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  except:
    limparConsole()
    print(f'Ocorreu um erro com a palavra {palavra}...')
    # erro = f'Na função: campoSemantico, usando {nome_modelo_escolhido}.\nDescrição do erro --> '+str(sys.exc_info()[0].__name__)+": "+str(sys.exc_info()[1])+'.'
    # with open('Problemas durante execução.txt','a',encoding='utf-8') as f:
    #   f.write(erro+'\n\n')
  else:
    limparConsole()
    print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Vizinhos mais próximos','-->',palavra_central,'\n\n')
    plt.clf()


def MapaDeCalorSimilaridadesAoDecorrerDoTempo(modelos_treinados,pasta_para_salvar=PASTA_SAVE_IMAGENS):
  
  print('\n\n\tVocê está montando uma visualização para Mapa de Calor ao decorrer do tempo.\n\n')
  palavra_central = input('Digite a palavra central: ').lower().strip()

  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra_central):
    palavra_central = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra palavra: ').lower().strip()

  palavras_selecionadas = []

  while True:
    palavra_digitada = input('Digite a palavra para ser comparada com a palavra central (0 para parar): ').lower().strip()
    if palavra_digitada != '0':
      palavras_selecionadas.append(palavra_digitada)
    else:
      break


  data = {}

  for nome_modelo_escolhido,modelo in modelos_treinados:
    dic_comparativo = {}
    for palavra_selecionada in palavras_selecionadas:
      try:
        dic_comparativo[palavra_selecionada] = modelo.similarity(palavra_central,palavra_selecionada)
      except:
        dic_comparativo[palavra_selecionada] = 0
    data[re.search(r'(\d{4})\_\d{4}',nome_modelo_escolhido).group(1) + '\n-\n' + re.search(r'\d{4}\_(\d{4})',nome_modelo_escolhido).group(1)] = dic_comparativo




  df = pd.DataFrame(data)

  plt.figure(figsize=(16, 8))
  heatmap = sns.heatmap(df, annot=True, cmap='coolwarm')

  heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0)
  heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0,fontsize=11)

  plt.title(f'Mapa de calor da similaridade para palavra "{palavra_central}"',fontsize=20)
  
  limparConsole()

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Mapas de Calor',palavra_central)

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
  
  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Mapa de Calor para {palavra_central}.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')
  
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Mapas de Calor','-->',palavra_central,'\n\n')
  
  plt.clf()
  # plt.show()



def Filtro(palavras : list,
           condicoes : list[str] = ['maior que 3 letras','remover stopwords','remover verbos','somente verbos']):
  
  str_remocao = ''
  remover_palavras = []
  for palavra in palavras:
    if (palavra[0] in PONTUACOES or palavra[-1] in PONTUACOES) and palavra not in remover_palavras:
      remover_palavras.append(palavra)
  if remover_palavras:
    for palavra in remover_palavras:
      palavras.remove(palavra)
      str_remocao += palavra+', '
    remover_palavras = []
  
  if 'maior que 3 letras' in condicoes:
    for palavra in palavras:
      if len(palavra)<=3 and palavra not in remover_palavras:
        remover_palavras.append(palavra)
    if remover_palavras:
      for palavra in remover_palavras:
        palavras.remove(palavra)
        str_remocao += palavra+', '
      remover_palavras = []

  if 'remover stopwords' in condicoes:
    # remover_palavras += [palavra for palavra in palavras if palavra in LISTA_STOP_WORDS and palavra not in remover_palavras]
    for palavra in palavras:
      if palavra in LISTA_STOP_WORDS and palavra not in remover_palavras:
        remover_palavras.append(palavra)
    if remover_palavras:
      for palavra in remover_palavras:
        palavras.remove(palavra)
        str_remocao += palavra+', '
      remover_palavras = []

  if 'remover verbos' in condicoes and 'somente verbos' not in condicoes:
    try:
      for palavra in palavras:
        if nlp(palavra)[0].pos_ in ['VERB','AUX'] and palavra not in remover_palavras:
          remover_palavras.append(palavra)
      if remover_palavras:
        for palavra in remover_palavras:
          palavras.remove(palavra)
          str_remocao += palavra+', '
        remover_palavras = []
    except Exception as e:
      erro = f'{e.__class__.__name__}: {str(e)}'
      print(f'\n\n\t! Problema ao filtrar verbos...\n\t! Por favor, certifique-se de ter instalado apropriadamente a biblioteca spaCy e as dependências necessárias.\n\t! Qualquer dúvida entre em contato com o Grupo de Estudos e Pesquisa em IA e História da UFSC.\n\t! Info do erro:{erro}\n\n')
      print('Aguardando 5s...\n')
      time.sleep(5)

  if 'somente verbos' in condicoes and 'remover verbos' not in condicoes:
    try:
      for palavra in palavras:
        if nlp(palavra)[0].pos_ not in ['VERB','AUX'] and palavra not in remover_palavras:
          remover_palavras.append(palavra)
      if remover_palavras:
        for palavra in remover_palavras:
          palavras.remove(palavra)
          str_remocao += palavra+', '
        remover_palavras = []
    except Exception as e:
      erro = f'{e.__class__.__name__}: {str(e)}'
      print(f'\n\n\t! Problema ao filtrar verbos...\n\t! Por favor, certifique-se de ter instalado apropriadamente a biblioteca spaCy e as dependências necessárias.\n\t! Qualquer dúvida entre em contato com o Grupo de Estudos e Pesquisa em IA e História da UFSC.\n\t! Info do erro:{erro}\n\n')
      print('Aguardando 5s...\n')
      time.sleep(5)

  return palavras,str_remocao[:-2]


def FrequenciaDePalavrasAoDecorrerDoTempo(modelos_treinados, pasta_para_salvar=PASTA_SAVE_IMAGENS):

  limparConsole()
  print('Escolha que tipo de frequência que você quer usar:\n')
  print('1 - Top 20 palavras mais frequentes')
  print('2 - Frequência de palavras específicas')

  resposta = input('\nDigite o número referente à sua escolha: ').strip()
  resposta = obterResposta(resposta=resposta,qtd_respostas=2,contagem_normal=True)
  

  if resposta == 1:
    limparConsole()
  
    print('Escolha, se quiser, quais filtros você gostaria de aplicar à resposta:\n')
    print('1 - Mostrar somente palavras com mais de 3 letras')
    print('2 - Remover stopwords')
    print('3 - Remover verbos')
    print('4 - Mostrar somente os verbos')
    print('5 - Não quero aplicar nenhum filtro, quero a resposta nua e crua!')
    
    resposta_filtro = input('\nDigite os números correspondentes separados por "," (vírgula) em caso de mais de uma resposta:\n').strip()
    if ',' in resposta_filtro:
      while len([r for r in resposta_filtro.split(',') if not r.isdigit()])>0:
          resposta_filtro = input('Por favor, reescreva uma resposta válida (só números): ')
      resposta_filtro = obterResposta(resposta=resposta_filtro,qtd_respostas=5,contagem_normal=True)
    else:
      if resposta_filtro != '5':
        resposta_filtro = obterResposta(resposta=resposta_filtro,qtd_respostas=5,contagem_normal=True)
      else:
        resposta_filtro = int(resposta_filtro)

    
    condicoes_filtro = []
    if resposta_filtro != 5:
      resposta_filtro = str(resposta_filtro)
      if '1' in resposta_filtro:
        condicoes_filtro.append('maior que 3 letras')
      if '2' in resposta_filtro:
        condicoes_filtro.append('remover stopwords')
      if '3' in resposta_filtro:
        condicoes_filtro.append('remover verbos')
      if '4' in resposta_filtro:
        condicoes_filtro.append('somente verbos')


    for modelo in modelos_treinados:
      FrequenciaDePalavrasTop20(tupla_modelo_escolhido=modelo,
                                pasta_para_salvar=pasta_para_salvar,
                                condicoes_filtro = condicoes_filtro)
  elif resposta == 2:
    FrequenciaDePalavrasSelecionadasAoDecorrerDoTempo(modelos_treinados=modelos_treinados)


def FrequenciaDePalavrasSelecionadasAoDecorrerDoTempo(modelos_treinados : list[tuple],pasta_para_salvar=PASTA_SAVE_IMAGENS):
  
  limparConsole()
  print('\n\n\tVocê está montando uma visualização para Frequência de Palavras Selecionadas ao decorrer do tempo.\n\n')
  
  lista_palavras = []

  cores = ['green','red','cyan','violet','blue','gold','orange','c','black','purple','lime','tomato','magenta','lightslategrey','lightgreen','paleturquoise','aquamarine','moccasin','lightcoral','chocolate','sandybrown','rosybrown']

  palavra_freq = input('Digite a primeira palavra: ').lower().strip()
  while True:
    while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra_freq) and palavra_freq != '0':
      palavra_freq = input('\n! Esta palavra não está presente em todos os modelos.\n! Por favor, digite outra palavra: ').lower().strip()
    if palavra_freq != '0':
      if palavra_freq not in lista_palavras:
        lista_palavras.append(palavra_freq)
    else:
      break
    if len(lista_palavras) == len(cores):
      break
    else:
      palavra_freq = input('\nDigite mais uma palavra (0 para parar): ').lower().strip()     
  
  nomes = [re.search(r'(\d{4})\_\d{4}',modelo[0]).group(1) + '\n-\n' + re.search(r'\d{4}\_(\d{4})',modelo[0]).group(1) for modelo in modelos_treinados]

  fig, ax = plt.subplots(figsize=(16, 8))

  x = [i+1 for i in range(len(modelos_treinados))]

  cores_usadas = []
  for palavra in lista_palavras:
    i = 0
    cor = cores[i]
    while cor in cores_usadas:
      cor = cores[i+1]
      i += 1
    cores_usadas.append(cor)
    y = []
    for modelo in [modelo[1] for modelo in modelos_treinados]:
      y.append(modelo.get_vecattr(palavra,'count'))

    ax.scatter(x, y, color='black', s=10)
    line_x = [x[0]] + x[1:-1] + [x[-1]]
    line_y = [y[0]] + y[1:-1] + [y[-1]]
    ax.plot(line_x, line_y, label=palavra, color=cor)
    for i in range(len((y))):
      ax.text(x[i], y[i]+0.01, str(round(y[i],2)), fontsize=6, ha='center', va='bottom')

  nome_modelo = re.sub(r'\_\d{4}\_\d{4}', '', modelos_treinados[0][0])

  ax.set_title(f'Frequência das palavras selecionadas\n{nome_modelo}', fontsize=20, pad= 25)
  ax.set_xlabel('Intervalos de tempo', fontsize=15, labelpad=20)
  ax.set_ylabel('Frequência', fontsize=15, labelpad=20)

  ax.set_xticks(x)
  ax.set_xticklabels(nomes,fontsize=11)

  ax.grid('on')
  ax.legend(fontsize = 11,loc='center left', bbox_to_anchor=(1, 0.5))
  plt.tight_layout(rect=[0, 0, 0.85, 1])

  limparConsole()

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Frequências de Palavras Selecionadas')

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)

  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Freq_selecionadas_{nome_modelo}_{"_".join(lista_palavras[:3])}_etc.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  plt.clf()
  # plt.show()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Frequências de Palavras Selecionadas','\n\n')
 
    
def FrequenciaDePalavrasTop20(tupla_modelo_escolhido,
                              condicoes_filtro : list[str] = [],
                              pasta_para_salvar : str = PASTA_SAVE_IMAGENS):
  nome_modelo_escolhido,modelo = tupla_modelo_escolhido
  plt.figure(figsize=(20, 10))

  # plt.bar([word for word in [palavra for palavra in modelo.wv.index_to_key[:500] if (palavra not in ['como','uma','um','ao','mais','mesmo','forma','pois','essa','apenas','parte','além','nesse']) and (nlp_spacy(palavra)[0].pos_ not in ['VERB','AUX']) and (len(palavra)>3)][:20]],[modelo.wv.get_vecattr(word,'count') for word in [palavra for palavra in modelo.wv.index_to_key[:500] if (palavra not in ['como','uma','um','ao','mais','mesmo','forma','pois','essa','apenas','parte','além','nesse']) and (nlp_spacy(palavra)[0].pos_ not in ['VERB','AUX']) and (len(palavra)>3)][:20]])  

  # dic_vocab_freq = {palavra:modelo.get_vecattr(palavra,'count') for palavra in modelo.index_to_key[:500]}
  tokens_filtrados,str_palavras_removidas = Filtro(palavras=modelo.index_to_key[:500],condicoes=condicoes_filtro)
  dic_vocab_freq = {palavra:modelo.get_vecattr(palavra,'count') for palavra in tokens_filtrados}

  dic_vocab_freq_ordenado = dict(sorted(dic_vocab_freq.items(), key=lambda item: item[1], reverse=True))
  
  # palavras_filtradas,str_palavras_removidas = Filtro(palavras=list(dic_vocab_freq_ordenado.keys()),condicoes=condicoes_filtro)
  palavras_filtradas = list(dic_vocab_freq_ordenado.keys())

  lista_palavras = [palavra for palavra in palavras_filtradas][:20]

  plt.bar([palavra for palavra in lista_palavras],[modelo.get_vecattr(palavra,'count') for palavra in lista_palavras])
  
  plt.xticks(rotation=45, ha='right')

  plt.title(f"Frequência de palavras treinamento {nome_modelo_escolhido}",fontsize=20)

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Frequência de Palavras')

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
    
  if condicoes_filtro:
    caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Freq_{nome_modelo_escolhido}_filtrado.png')  
  else:
    caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Freq_{nome_modelo_escolhido}_sem_filtro.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  limparConsole()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Frequência de Palavras','\n\n')
  if str_palavras_removidas != '':
    print('Os seguintes tokens foram removidos das visualizações:',str_palavras_removidas)

  plt.clf()



def EstratosDoTempo(modelos_treinados,pasta_para_salvar=PASTA_SAVE_IMAGENS):
  def pega_cor(bg_color):
      gray = np.dot(bg_color, [0.2989, 0.5870, 0.1140])
      return 'black' if gray > 0.5 else 'white'

  def agrupar_em_trios(lista):
      lista_nova = [(lista[i], lista[i + 1], lista[i + 2]) for i in range(0, len(lista), 3)]
      return lista_nova
  
  print('\n\n\tVocê está montando uma visualização para Estratos do Tempo.\n\n')
  palavra_central = input('Digite a palavra central: ').lower().strip()

  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra_central):
    palavra_central = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra palavra: ').lower().strip()

  data = {}

  for nome_modelo, modelo in modelos_treinados:

    ano_inicial = re.search(r'(\d{4})\_\d{4}',nome_modelo).group(1)
    ano_final = re.search(r'\d{4}\_(\d{4})',nome_modelo).group(1)

    chave = ano_inicial + ' - ' + ano_final

    lista_valores = [{r[0]:r[1]} for r in modelo.most_similar(palavra_central)]

    data[chave] = lista_valores


  lista_de_tuplas = list(data.items())
  lista_de_tuplas_invertida = lista_de_tuplas[::-1]
  data = dict(lista_de_tuplas_invertida)


  index = list(data.keys())
  values = [[list(d.values())[0] for d in data[key]] for key in data]

  heatmap_values = [[list(data[key][0].values())[0]] for key in data]
  df = pd.DataFrame(heatmap_values, index=index)

  plt.figure(figsize=(8, 8))
  heatmap = sns.heatmap(df, annot=False, fmt="", cmap='coolwarm', cbar=True, cbar_kws={'shrink': 0.8})
  # heatmap = sns.heatmap(df, annot=False, fmt="", cmap='coolwarm', cbar=True, cbar_kws={'shrink': 0.8}, linewidths=1, linecolor='black')

  nome_modelo_atual = re.sub(r'\_\d{4}\_\d{4}','',modelos_treinados[0][0])

  for i in range(len(df.index)):
      key = df.index[i]
      principal_key = list(data[key][0].keys())[0]
      principal_value = round(list(data[key][0].values())[0],4)
      
      lista_nova = agrupar_em_trios(data[key][1:])
      other_keys_values = [f"{list(c.keys())[0]}: {round(list(c.values())[0],4)} / {list(d.keys())[0]}: {round(list(d.values())[0],4)} / {list(b.keys())[0]}: {round(list(b.values())[0],4)}" for c,d,b in lista_nova]
      bg_color = heatmap.get_children()[0].get_facecolor()[i][:3]
      text_color = pega_cor(bg_color)

      plt.text(0.5, i + 0.2, f"{principal_key}: {principal_value}", ha='center', va='center', fontsize=12, weight='bold',
              color=text_color)
      for j, line in enumerate(other_keys_values):
          plt.text(0.5, i + 0.45 + j * 0.15, line, ha='center', va='center', fontsize=8, color=text_color)

  plt.xticks([])
  heatmap.set_yticklabels(sorted(list(df.index[::-1]),reverse=True), fontsize=12, rotation=0, weight='bold')

  plt.title(f'Estratos do Tempo\npara "{palavra_central}"\nusando {nome_modelo_atual}', fontsize=20, pad=30)
  plt.tight_layout()

  limparConsole()

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Estratos do Tempo',palavra_central)

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
  
  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Estratos do Tempo para {palavra_central}.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')
  
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Estratos do Tempo','-->',palavra_central,'\n\n')
  
  plt.clf()



def VetoresDePalavrasAoDecorrerDoTempo(modelos_treinados, pasta_para_salvar=PASTA_SAVE_IMAGENS):
  print('\n\n\tVocê está montando uma visualização para Vetores de Palavras ao decorrer do tempo.\n\n')

  lista_de_palavras = []
  palavra = input('Digite a primeira palavra: ').lower().strip()
  while palavra != '0':
    # while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra):
    #   print(f'A palavra "{palavra}" não está presente em todos os modelos, em algumas imagens ela não aparecerá.')      
    #   print('Caso queira substituí-la por outra, digite abaixo qual palavra a substituirá.')
    #   print('Se não quiser substituir, basta pressionar Enter')      
    #   resposta = input('\nResposta: ').lower().strip()
    #   if not resposta == '':
    #     palavra = resposta
        
    if palavra not in lista_de_palavras:
      lista_de_palavras.append(palavra)

    palavra = input('\nDigite mais uma palavra (0 para parar): ').lower().strip()

  for modelo in modelos_treinados:
    vetoresDePalavras(tupla_modelo_escolhido=modelo,
                      lista_de_palavras=lista_de_palavras,
                      pasta_para_salvar=pasta_para_salvar)


def vetoresDePalavras(tupla_modelo_escolhido,
                      lista_de_palavras : list[str],
                      pasta_para_salvar : str):

  nome_modelo_escolhido,modelo_escolhido = tupla_modelo_escolhido
  lista_de_palavras = [palavra for palavra in lista_de_palavras if palavra in modelo_escolhido.index_to_key]
  lista_de_vetores = [modelo_escolhido[palavra] for palavra in lista_de_palavras]

  pca = PCA(n_components=2)
  lista_de_vetores_2D = pca.fit_transform(lista_de_vetores)

  limite_pos_x = 0
  limite_neg_x = 0
  limite_pos_y = 0
  limite_neg_y = 0
  x = []
  y = []

  for coords in lista_de_vetores_2D:
    x.append(coords[0])
    if coords[0] > limite_pos_x:
      limite_pos_x = coords[0]
    elif coords[0] < limite_neg_x:
      limite_neg_x = coords[0]

    y.append(coords[1])
    if coords[1] > limite_pos_y:
      limite_pos_y = coords[1]
    elif coords[1] < limite_neg_y:
      limite_neg_y = coords[1]

  fig, ax = plt.subplots(1, 2,figsize=(12, 5),gridspec_kw={'width_ratios': [4, 1]})

  ax[0].grid('on')
  ax[1].axis('off')
  # ax[0].grid('off')

  for i, palavra in enumerate(lista_de_palavras):
      ax[0].arrow(0, 0, lista_de_vetores_2D[i, 0], lista_de_vetores_2D[i, 1], head_width=0.1, head_length=0.1, fc='blue', ec='blue')
      ax[0].text(lista_de_vetores_2D[i, 0], lista_de_vetores_2D[i, 1]+0.25, palavra, fontsize=12, ha='center', va='center', color='black')

  ax[0].set_xlim(limite_neg_x-1, limite_pos_x+1)
  ax[0].set_ylim(limite_neg_y-1, limite_pos_y+1)

  cosseno_formula = r'$\cos(\theta) = \frac{\mathbf{v} \cdot \mathbf{u}}{\|\mathbf{v}\| \cdot \|\mathbf{u}\|}$'

  ax[1].text(0.25, 0.5,cosseno_formula, fontsize=20, ha='center', va='center')

  ax[0].set_title(f'Vetores de palavras representados em 2D com {nome_modelo_escolhido}')
  ax[0].set_xlabel('Dimensão 1')
  ax[0].set_ylabel('Dimensão 2')

  
  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Vetores de palavras',', '.join(lista_de_palavras[:3])+' etc')

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
    
  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Vetores de palavras para {nome_modelo_escolhido} - {", ".join(lista_de_palavras[:3])+" etc"}.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png',' copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  limparConsole()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Vetores de palavras','\n\n')
  plt.clf()



def ComparacaoEntrePalavrasAoDecorrerDoTempo(modelos_treinados, pasta_para_salvar=PASTA_SAVE_IMAGENS):
  print('\n\n\tVocê está montando uma visualização para Comparacao Entre Palavras ao decorrer do tempo.\n\n')

  print('\n\nHomem --> Rei\n\nMulher --> X\n\n')

  homem = input('O que deseja substituir por "homem"? ').lower().strip()
  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=homem):
    homem = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra: ').lower().strip()

  rei = input('O que deseja substituir por "rei"? ')
  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=rei):
    rei = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra: ').lower().strip()
  
  mulher = input('O que deseja substituir por "mulher"? ')
  while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=mulher):
    mulher = input('Esta palavra não está presente em todos os modelos.\nPor favor, digite outra: ').lower().strip()      

  tupla_comparacao = (homem,rei,mulher)

  for modelo in modelos_treinados:
    ComparacaoEntrePalavras(tupla_modelo_escolhido=modelo,
                            tupla_comparacao=tupla_comparacao,
                            pasta_para_salvar=pasta_para_salvar)


def ComparacaoEntrePalavras(tupla_modelo_escolhido,
                            tupla_comparacao : tuple[str],
                            pasta_para_salvar : str):
  nome_modelo_escolhido, modelo_escolhido = tupla_modelo_escolhido
  homem,rei,mulher = tupla_comparacao
     
  lista_de_palavras = []
  lista_de_palavras.append(homem)
  lista_de_palavras.append(rei)
  lista_de_palavras.append(mulher)

  resultado = modelo_escolhido.most_similar_cosmul(positive=[rei,mulher], negative=[homem])
  
  lista_de_palavras.extend(r[0] for r in resultado)

  lista_de_palavras_e_suas_similaridades = [(r[0],r[1]) for r in resultado]

  lista_de_vetores_base = [[1,5],[5,7],[2,2],[6,4]]
  lista_de_vetores_adc = []

  for i,r in enumerate(resultado[1:]):
    if i ==0:
      raiox = 1-r[1] + 0.25
      raioy = 1-r[1] + 0.25
    elif i ==1:
      raiox = 1-r[1] -0.75
      raioy = 1-r[1] -0.5
    elif i ==2:
      raiox = 0
      raioy = 0.87
    elif i ==3:
      raiox = 1-r[1] + 0.5
      raioy = 1-r[1] -0.87
    elif i ==4:
      raiox = 1-r[1] +0.6
      raioy = 1-r[1] +0.5
    elif i ==5:
      raiox = 1-r[1] -0.9
      raioy = 1-r[1] +0.7
    elif i ==6:
      raiox = 1-r[1] + - 1
      raioy = 1-r[1] - 0
    elif i ==7:
      raiox = 1-r[1] +1.1
      raioy = 1-r[1] -0
    elif i ==8:
      raiox = 1-r[1] +1.2
      raioy = 1-r[1] -0.25
    lista_de_vetores_adc.append([6+raiox,4+raioy])


  lista_de_vetores_2D = lista_de_vetores_base
  lista_de_vetores_2D.extend(lista_de_vetores_adc)


  limite_pos_x = 0
  limite_neg_x = 0
  limite_pos_y = 0
  limite_neg_y = 0
  x = []
  y = []

  for coords in lista_de_vetores_2D:
    x.append(coords[0])
    if coords[0] > limite_pos_x:
      limite_pos_x = coords[0]
    elif coords[0] < limite_neg_x:
      limite_neg_x = coords[0]

    y.append(coords[1])
    if coords[1] > limite_pos_y:
      limite_pos_y = coords[1]
    elif coords[1] < limite_neg_y:
      limite_neg_y = coords[1]


  fig, ax = plt.subplots(1, 2,figsize=(12, 5),gridspec_kw={'width_ratios': [4, 1]})

  ax[0].grid('on')
  ax[0].axis('on')
  ax[1].axis('off')

  for i, palavra in zip(range(0,3),lista_de_palavras[0:3]):
    ax[0].scatter(x[i], y[i],color='b')
    ax[0].text(x[i], y[i]+0.25, palavra, fontsize=11, ha='center', va='center', color='black')
  for i, palavra in zip(range(3,len(lista_de_palavras)),lista_de_palavras[3:]):
    if i == 3:
      ax[0].scatter(x[i], y[i]-0.15,color='b')
      ax[0].text(x[i], y[i]-0.15+0.25, palavra, fontsize=10, ha='center', va='center', color='black')
    else:
      ax[0].scatter(x[i], y[i],color='g')
      ax[0].text(x[i], y[i]+0.25, palavra, fontsize=10, ha='center', va='center', color='black')

  ax[0].arrow(x[0],y[0],x[1]-x[0],y[1]-y[0],head_width=0.1, head_length=0.1, fc='red', ec='red')
  ax[0].arrow(x[2],y[2],x[3]-x[2],y[3]-y[2],head_width=0.1, head_length=0.1, fc='red', ec='red')


  ax[0].set_xlim(limite_neg_x-1, limite_pos_x+1)
  ax[0].set_ylim(limite_neg_y-1, limite_pos_y+1)


  ax[0].set_title(f'Vetores representados em 2D com {nome_modelo_escolhido}')
  ax[0].set_xlabel('Dimensão 1')
  ax[0].set_ylabel('Dimensão 2')

  texto = "Resultado:\n('palavra', similaridade)"
  for elemento_vet in lista_de_palavras_e_suas_similaridades:
    texto += '\n\n'+str(elemento_vet)

  ax[1].text(1, 0.5,texto, fontsize=11, ha='center', va='center')

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Comparação Entre Palavras',', '.join(tupla_comparacao)+', X')

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
    
  caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Comparação Entre Palavras para {nome_modelo_escolhido}.png')

  while os.path.exists(caminho_save_fig):  
    caminho_save_fig = caminho_save_fig.replace('.png',' copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  limparConsole()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Comparação Entre Palavras','\n\n')
  plt.clf()



def DistanciaEntreVetores(a,b):
  A = np.array([a])
  B = np.array([b])
  return np.linalg.norm(A - B)

def SimilaridadePorCosseno(a,b):
  A = np.array([a])
  B = np.array([b])
  return cosine_similarity(A,B)[0][0]

def MudancaDePalavrasAoDecorrerDoTempo(modelos_treinados : list[tuple], pasta_para_salvar : str = PASTA_SAVE_IMAGENS):
  limparConsole()
  print('Escolha que tipo de mudança você quer visualizar:\n')
  print('1 - Quero visualizar um apanhado geral de todas as palavras')
  print('2 - Quero visualizar para palavras específicas')

  resposta_1 = input('\nDigite o número referente à sua escolha: ').strip()
  resposta_1 = obterResposta(resposta=resposta_1,qtd_respostas=2,contagem_normal=True)

  condicoes_filtro = []
  lista_palavras = []

  if resposta_1 == 1:
    limparConsole()
  
    print('Escolha, se quiser, quais filtros você gostaria de aplicar à resposta:\n')
    print('1 - Mostrar somente palavras com mais de 3 letras')
    print('2 - Remover stopwords')
    print('3 - Remover verbos')
    print('4 - Mostrar somente os verbos')
    print('5 - Não quero aplicar nenhum filtro, quero a resposta nua e crua!')
    
    resposta_filtro = input('\nDigite os números correspondentes separados por "," (vírgula) em caso de mais de uma resposta:\n').strip()
    if ',' in resposta_filtro:
      while len([r for r in resposta_filtro.split(',') if not r.isdigit()])>0:
          resposta_filtro = input('Por favor, reescreva uma resposta válida (só números): ')
      resposta_filtro = obterResposta(resposta=resposta_filtro,qtd_respostas=5,contagem_normal=True)
    else:
      if resposta_filtro != '5':
        resposta_filtro = obterResposta(resposta=resposta_filtro,qtd_respostas=5,contagem_normal=True)
      else:
        resposta_filtro = int(resposta_filtro)
    
    if resposta_filtro != 5:
      resposta_filtro = str(resposta_filtro)
      if '1' in resposta_filtro:
        condicoes_filtro.append('maior que 3 letras')
      if '2' in resposta_filtro:
        condicoes_filtro.append('remover stopwords')
      if '3' in resposta_filtro:
        condicoes_filtro.append('remover verbos')
      if '4' in resposta_filtro:
        condicoes_filtro.append('somente verbos')

  elif resposta_1 == 2:
    limparConsole()
    palavra = input('Digite a primeira palavra: ').lower().strip()
    while True:
      while not verificaExistenciaNosModelos(modelos_treinados=modelos_treinados,palavra_central=palavra) and palavra != '0':
        palavra = input('\n! Esta palavra não está presente em todos os modelos.\n! Por favor, digite outra palavra: ').lower().strip()
      if palavra != '0':
        if palavra not in lista_palavras:
          lista_palavras.append(palavra)
      else:
        break      
      palavra = input('\nDigite mais uma palavra (0 para parar): ').lower().strip()

  limparConsole()
  print('Escolha que tipo de taxa de mudança que você quer usar:\n')
  print('1 - Taxa percentual usando apenas da similaridade de cosseno entre dois períodos')
  print('(Ñ DISPONÍVEL) 2 - Taxa percentual usando da Similaridade acumulada entre dois períodos (considera os períodos do meio)')
  print('(Ñ DISPONÍVEL) 3 - Taxa percentual usando índice de Jaccard')
  print('(Ñ DISPONÍVEL) 4 - Distância entre dois períodos')

  resposta_2 = input('\nDigite o número referente à sua escolha: ').strip()
  resposta_2 = obterResposta(resposta=resposta_2,qtd_respostas=4,contagem_normal=True)
  
  limparConsole()
  print('Escolha qual início (primeiro modelo) e fim (último modelo) a ser considerado:\n')
  for i, modelo in enumerate([m[0] for m in modelos_treinados]):
    print(f'{i+1} - {modelo}')

  resposta_3 = input('\nDigite o número referente os números referentes à sua escolha, separados por vírgula e seguindo a ordem "primeiro, último":\n').strip()
  while ',' not in resposta_3:
    resposta_3 = input('\nPor favor, digite os números referente os números referentes à sua escolha, SEPARADOS POR VÍRGULA e seguindo a ordem "PRIMEIRO MODELO, ÚLTIMO MODELO":\n').strip()
  while len([r for r in resposta_3.split(',') if not r.isdigit()])>0:
    resposta_3 = input('\nPor favor, digite OS NÚMEROS referente os números referentes à sua escolha, SEPARADOS POR VÍRGULA e seguindo a ordem "PRIMEIRO MODELO, ÚLTIMO MODELO":\n').strip()
    while ',' not in resposta_3:
      resposta_3 = input('\nPor favor, digite os números referente os números referentes à sua escolha, SEPARADOS POR VÍRGULA e seguindo a ordem "PRIMEIRO MODELO, ÚLTIMO MODELO":\n').strip()

  resposta_3 = obterResposta(resposta=resposta_3,qtd_respostas=len(modelos_treinados),contagem_normal=False)

  primeiro_modelo = modelos_treinados[resposta_3[0]]
  ultimo_modelo = modelos_treinados[resposta_3[-1]]


  if resposta_2 == 1:
    TaxaSimilaridadeCosseno(modelo_inicial=primeiro_modelo,
                            modelo_final=ultimo_modelo,
                            lista_de_palavras=lista_palavras,
                            condicoes_filtro=condicoes_filtro)


def CalcularTaxaMudancaPelaSimilaridade(similaridade):
    # if similaridade < -1 or similaridade > 1:
    #     raise ValueError("O valor deve estar no intervalo de -1 a 1.")
    taxa = -50 * similaridade + 50
    return round(taxa,4)

def TaxaSimilaridadeCosseno(modelo_inicial,
                            modelo_final,
                            lista_de_palavras : list[str],
                            condicoes_filtro : list[str] = [],
                            pasta_para_salvar=PASTA_SAVE_IMAGENS):
  limparConsole()
  nome_primeiro_modelo, primeiro_modelo = modelo_inicial
  nome_ultimo_modelo, ultimo_modelo = modelo_final

  str_palavras_removidas = ''
  if not lista_de_palavras:
    taxa_global = True
    print('Contabilizando todos os tokens...\nPor favor, aguarde!')
    tokens_filtrados,str_palavras_removidas = Filtro(palavras=primeiro_modelo.index_to_key,condicoes=condicoes_filtro)
    lista_de_palavras = [palavra for palavra in tokens_filtrados]
  else:
    taxa_global = False

  dic_mudanca = {}
  for palavra in lista_de_palavras:
    dic_mudanca[palavra] = CalcularTaxaMudancaPelaSimilaridade(similaridade=SimilaridadePorCosseno(primeiro_modelo[palavra], ultimo_modelo[palavra]))

  dicionario_ordenado = dict(sorted(dic_mudanca.items(), key=lambda item: item[1],reverse=True))

  if taxa_global:
    palavras = list(dicionario_ordenado.keys())[:20]
    numeros = list(dicionario_ordenado.values())[:20]
  else:
    palavras = list(dicionario_ordenado.keys())
    numeros = list(dicionario_ordenado.values())
  

  plt.figure(figsize=(20, 10))

  plt.gca().set_facecolor('ivory')

  bars = plt.bar(palavras, numeros, color='darkorchid') #['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']

  plt.title(f'Maiores mudança dos vetores ao decorrer dos treinamentos\n{nome_primeiro_modelo} até {nome_ultimo_modelo}', fontsize=20, fontweight='bold', pad = 30)
  plt.xlabel('Vetores de palavras', fontsize=16)
  plt.ylabel('Porcentagem de mudança [%]', fontsize=16)

  plt.xticks(rotation=45, ha='right', fontsize=12)

  plt.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)

  for bar in bars:
      bar.set_edgecolor('black')
      bar.set_linewidth(1)

  primeiro_ano_inicial = re.search(r'(\d{4})\_\d{4}',nome_primeiro_modelo).group(1)
  ultimo_ano_final = re.search(r'\d{4}\_(\d{4})',nome_ultimo_modelo).group(1)

  pasta_para_salvar_palavra_central = os.path.join(pasta_para_salvar,'Taxa Percentual Mudança pela Similaridade por Cosseno')

  if not os.path.exists(pasta_para_salvar_palavra_central):
    os.makedirs(pasta_para_salvar_palavra_central)
      
  if condicoes_filtro:
    # caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Mudança todas as palavras para {primeiro_ano_inicial} e {ultimo_ano_final} filtro de {" e ".join(condicoes_filtro)}.png')  
    caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Mdnc_todas_{primeiro_ano_inicial}_{ultimo_ano_final}_filtrado.png')  
  else:
    if taxa_global:
      caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Mdnc_todas_{primeiro_ano_inicial}_{ultimo_ano_final}_sem_filtro.png')
    else:
      caminho_save_fig = os.path.join(pasta_para_salvar_palavra_central,f'Mdn_selecionadas_{primeiro_ano_inicial}_{ultimo_ano_final}.png')

  while os.path.exists(caminho_save_fig):
    caminho_save_fig = caminho_save_fig.replace('.png','_copia.png')

  plt.savefig(caminho_save_fig, dpi=300, bbox_inches='tight')

  limparConsole()
  print('\n\n\tImagem salva em',PASTA_SAVE_IMAGENS,'-->','Taxa Percentual Mudança pela Similaridade por Cosseno','\n\n')
  if str_palavras_removidas != '':
    print('Os seguintes tokens foram removidos das visualizações:',str_palavras_removidas)

  plt.clf()


# def TaxaSimilaridadeCossenoAcumulada():


# def TaxaIndiceJaccard():


# def DistanciaEntrePalavras():

def obterListaStopWords(caminho_arquivo_lista_stopwords : str = r'visualizacoes_woke\lista_stopwords.txt'):
  try:
    lista_stopwords = []
    if caminho_arquivo_lista_stopwords.endswith('.txt'):
      with open(caminho_arquivo_lista_stopwords,'r',encoding='utf-8') as f:
        stopwords = f.read()

      lista_stopwords = [palavra.strip() for palavra in stopwords.split('\n') if not (palavra.startswith('#') or palavra.startswith('-'))]  
      lista_stopwords = sorted(set([palavra.strip() for palavra in stopwords.split('\n') if not (palavra.startswith('#') or palavra.startswith('-'))]),key=len)
      return lista_stopwords
    else:    
      print('\n\n\t! Lista de stopwords deve estar no formato ".txt"!\n\t! Além disso deve-se seguir o padrão de separar as palavras por quebra de linha.\n\n')
      print('Aguardando 5s...\n')
      time.sleep(5)
      return []
  except Exception:
    return '''#Artigos
o
os
a
as
ao
aos
uns
umas
#Preposições
à
às
aos
da
das
do
dos
no
nos
na
nas
numa
numas
num
nuns
dessa
dessas
desse
desses
desta
destas
deste
destes
ante
até
após
com
contra
de
desde
em
entre
para
perante
por
sem
sob
sobre
trás
conforme
consoante
mediante
tirante
senão
#Pronomes
eu
tu
ele
eles
ela
elas
nós
vós
me
te
lhe
lhes
se
nos
vos
mim
comigo
ti
contigo
si
consigo
nós
conosco
vós
convosco
você
meu
minha
meus
minhas
teu
tua
teus
tuas
seu
sua
seus
suas
nosso
nossa
nossos
nossas
vosso
vossa
vossos
vossas
este
isto
esse
isso
aquele
aquilo
algum
alguma
alguns
algumas
nenhum
nenhuma
nenhuns
nenhumas
outro
outra
outros
outras
todo
toda
todos
todas
vário
vária
vários
várias
muito
muita
muitos
muitas
pouco
pouca
poucos
poucas
qualquer
quaisquer
qual
quais
quanto
quanta
quantos
quantas
alguém
ninguém
outrem
quem
algo
tudo
nada
cada
que
qual
quais
quanto
quanta
quantos
quantas
cujo
cuja
cujos
cujas
onde
esse
esses
essa
essas
esta
estas
este
estes
#Conjunções
mas
e
também
só
todavia
ou
-seja
portanto
logo
porque
que
assim
já
embora
ainda
conforme
depois
antes
afim
quanto
quantos
quanta
quantas
porém
contudo
entretanto
outrossim
#Extras
mesmo
mesmos
mesma
mesmas
como
tal
aqui
pois
pela
pelas
pelo
pelos
parte
além
mais
menos
qual
quais
quando
quem
aquele
àquele
aqueles
àqueles
aquela
àquela
aquelas
àquelas
aquilo
àquilo
naquele
naqueles
naquela
naquelas
naquilo
nesse
nesses
nessa
nessas
apenas
tipo
sim
não
aí
meio
maior
menor
igual
forma
primeiro
segundo
terceiro
quarto
quinto
#Numerais
um
uma
dois
duas
três
quatro
cinco
seis
sete
oito
nove
dez
onze
doze
treze
quatorze
quinze'''

LISTA_STOP_WORDS = obterListaStopWords()

