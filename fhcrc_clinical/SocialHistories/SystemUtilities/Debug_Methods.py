def write_training_data_as_file(training_sents, training_labels, sent_objs):
    with open ("/home/wlane/Documents/Substance_IE_Data/Debug/training_data.CRFSuite.debug", "wb") as f:
        for i in range(0, len(training_sents), 1):
            f.write(sent_objs[i].id)
            f.write("\n\t"+ str(training_sents[i]) + "\n\t" + str(training_labels[i]) + "\n\n")

def write_status_classf_vecs_to_file(labels, vectors):
    with open ("/home/wlane/Documents/Substance_IE_Data/Debug/training_vecs.status_classf.debug", "wb") as f:
        for i in range(0,len(vectors)-1,1):
            f.write(str(labels[i]) + ": " +str(vectors[i]) + "\n")
