import pickle
import numpy

from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Activation

NOTE_TYPE = {
    "eighth": 0.5,
    "quarter": 1,
    "half": 2,
    "16th": 0.25
}

def generate():
    """Generate a piano a MIDI file"""

    with open("data/notes", 'rb') as filepath:
        notes = pickle.load(filepath)

    # Get all pitch names
    pitch_names = sorted(set(item for item in notes))
    n_vocab = len(set(notes))

    network_input, normalized_input = prepare_sequences(notes, pitch_names, n_vocab)
    model = create_network(normalized_input, n_vocab)
    prediction_output = generate_notes(model, network_input, pitch_names, n_vocab)
    create_midi(prediction_output)

def prepare_sequences(notes, pitch_names, n_vocab):
    """Prepare the sequences used by the Neural Network"""
    
    # Map between notes and integers and back
    note_to_int = dict((note, number) for number, note in enumerate(pitch_names))

    sequence_length = 100
    network_input = []
    output = []

    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # Reshape the input into a format compatible with LSTM layers
    normalized_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))

    # Normalize input
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)


def create_network(network_input, n_vocab):
    """ create the structure of the neural network """
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        recurrent_dropout=0.3,
        return_sequences=True
    ))
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3,))
    model.add(LSTM(512))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    # Load the weights to each node
    # TODO: Select the latest weights file...
    model.load_weights('./weights/updated-lofi-hip-hop-weights-improvement-1396-0.0743.hdf5')

    return model

def generate_notes(model, network_input, pitch_names, n_vocab):
    """Generate notes from the Neural network based on a sequence of notes"""

    # Pick a random sequence from the input as a starting point for the prediction
    start = numpy.random.randint(0, len(network_input) - 1)
    int_to_note = dict((number, note) for number, note in enumerate(pitch_names))

    pattern = network_input[start]
    prediction_output = []

    # Generate 500 notes
    for note_index in range(500):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:len(pattern)]
    
    return prediction_output


def create_midi(prediction_output):
    """
    Convert the output from the prediction to notes and create a MIDI 
    file from the notes
    """

    offset = 0
    output_notes = []

    # Create note and chord objects based on the values generated by the model
    for pattern in prediction_output:

        curr_type = numpy.random.choice(list(NOTE_TYPE.keys()), p=[0.65, 0.05, 0.05, 0.25])
        # Pattern is a chord
        if ("." in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split(".")
            notes = []

            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            
            new_chord = chord.Chord(notes, type=curr_type)
            new_chord.offset = offset
            output_notes.append(new_chord)
        
        elif str(pattern).upper() == "R":
            curr_type = "16th"
            new_rest = note.Rest(type=curr_type)
            new_rest.offset = offset
            output_notes.append(new_rest)

        # Pattern is a note
        else:
            new_note = note.Note(pattern, type=curr_type)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)
        
        # Increase offset each iteration so notes DO NOT stack
        offset += NOTE_TYPE[curr_type]
    
    midi_stream = stream.Stream(output_notes)
    midi_stream.write("midi", fp="lofi_output.mid")


if __name__ == "__main__":
    generate()