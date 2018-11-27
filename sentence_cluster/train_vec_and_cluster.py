# -*-coding:utf-8-*-

import pickle

import jieba
import gensim
from sklearn.cluster import KMeans
from sklearn.externals import joblib

def read_pickle_file(file_path):
    with open(file_path, "rb") as fp:
        data_lines = pickle.load(fp)
    return data_lines

#read file and seperate words
def cut_words_write(data_lines, cut_file_name):
    with open(cut_file_name, 'w', encoding='utf-8') as pfw:
        for each_ls in data_lines:
            line = each_ls[0] + each_ls[1]
            line = line.strip('\n')
            seg_list = jieba.cut(line)
            pfw.write(' '.join(seg_list)+'\n')

def train_vec_model(cut_file_name, vector_size, window, vec_file):
    sentences = gensim.models.doc2vec.TaggedLineDocument(cut_file_name)
    model = gensim.models.Doc2Vec(sentences, vector_size=vector_size, window=window)
    model.train(sentences, epochs=20, total_examples=model.corpus_count)
    model.save(vec_file)
    return model

def train_cluster(data_lines, model, num_clusters, model_file):
    km = KMeans(n_clusters=num_clusters)  #设置模型参数
    infered_vectors_list = []
    for text in data_lines:
        vector = model.infer_vector(text[0]+text[1])
        infered_vectors_list.append(vector)
    result = km.fit_predict(infered_vectors_list)  #用doc2vec训练的模型产生的句向量作为k-means的输入
    joblib.dump(km, model_file)
    return result

def write_doc_cluster(num_clusters, cluster_result, data_lines, out_put_dir):
    for i in range(num_clusters):
        cluster_file_name = "{}/cluster_{}.pkl".format(out_put_dir, str(i))
        tmp_doc_cluster_ls = []
        with open(cluster_file_name, 'wb') as pfw:
            for line_number, each_line in enumerate(data_lines):
                if line_number >= len(cluster_result):
                    break
                if cluster_result[line_number] == i:
                    tmp_doc_cluster_ls.append([each_line[0], each_line[1]])
            pickle.dump(tmp_doc_cluster_ls, pfw)

if __name__ == '__main__':
    # data_lines = read_pickle_file("../data/all_data.pkl")
    # cut_words_write(data_lines, 'output.seq')
    # model = train_vec_model('output.seq', 200, 4, "../vec_model/doc_vec")
    # cluster_result = train_cluster(data_lines, model, 10, "../cluster_model/kmeans.pkl")
    # write_doc_cluster(10, cluster_result, data_lines, "cluster_result")

    data_lines = read_pickle_file("drive/doc2vec/all_data.pkl")
    cut_words_write(data_lines, 'drive/doc2vec/output.seq')
    model = train_vec_model('drive/doc2vec/output.seq', 200, 4, "drive/doc2vec/doc_vec")
    cluster_result = train_cluster(data_lines, model, 10, "drive/doc2vec/kmeans.pkl")
    write_doc_cluster(10, cluster_result, data_lines, "drive/doc2vec/cluster_result")
