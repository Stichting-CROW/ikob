import ikob.Routines as Routines


def bereken_concurrentie(Matrix, Beroepsbevolking, Bereik, inkgr, inkgroepen):
    Dezegroeplijst = []
    Beroepsbevolkingtrans = Routines.transponeren(Beroepsbevolking)
    for i in range(len(Matrix)):
        Gewogenmatrix = []
        for Getal1, Getal2, Getal3 in zip(Matrix[i], Bereik, Beroepsbevolkingtrans[inkgroepen.index(inkgr)]):
            if Getal2 > 0:
                Gewogenmatrix.append(Getal1*Getal3/Getal2)
            else:
                Gewogenmatrix.append(0)
        Dezegroeplijst.append(sum(Gewogenmatrix))
    return Dezegroeplijst


def bereken_potenties(Matrix, Inwonerstrans, gr, Groepen):
    Dezegroeplijst = []
    for i in range(len(Matrix)):
        Gewogenmatrix = []
        for Getal1, Getal2 in zip(Matrix[i], Inwonerstrans[Groepen.index(gr)]):
            Gewogenmatrix.append(Getal1 * Getal2)
        Dezegroeplijst.append(sum(Gewogenmatrix))
    return Dezegroeplijst
