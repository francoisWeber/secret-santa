from email import message


def get_senders_receivers_from_mat(gifts_matrix, peoples):
    senders_and_receivers = []
    for i, name in enumerate(peoples):
        receiver_of_i = gifts_matrix[i].argmax()
        senders_and_receivers.append([name, peoples[receiver_of_i]])
    return senders_and_receivers