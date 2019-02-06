class BPI13Flow(object):
    '''
    Actions an actor from the BPI13 workflow can follow.
    TODO: make this an abstract base class?
    '''
    def a_submitted(self):
        pass

    def a_partlysubmitted(self):
        pass

    def w_beoordelen_fraude_schedule(self):
        pass

    def w_beoordelen_fraude_start(self):
        pass

    def w_beoordelen_fraude_complete(self):
        pass

    def A_declined(self):
        pass

    def W_afhandelen_leads_schedule(self):
        pass

    def W_afhandelen_leads_start(self):
        pass

    def W_afhandelen_leads_complete(self):
        pass

    def A_preaccepted(self):
        pass

    def W_completeven_aanvraag_scheduled(self):
        pass

    def W_completeven_aanvraag_start(self):
        pass

    def W_completeven_aanvraag_complete(self):
        pass

    def W_wijzigen_contractgegevens_scheudle(self):
        pass

    def A_accepted(self):
        pass

    def A_finalised(self):
        pass

    def A_concalled(self):
        pass

    def O_selected(self):
        pass

    def C_created(self):
        pass

    def O_sent(self):
        pass

    def O_cancelled(self):
        pass

    def O_sent_back(self):
        pass

    def W_nabellen_offertes_scheduled(self):
        pass

    def W_nabellen_offertes_start(self):
        pass

    def W_nabellen_offertes_complete(self):
        pass

    def W_valideren_aanvraag_scheduled(self):
        pass

    def W_nabellen_incomplete_dossiers_scheduled(self):
        pass

    def W_nabellen_incomplete_dossiers_start(self):
        pass

    def W_nabellen_incomplete_dossiers_complete(self):
        pass


class CustomerServiceActor(BPI13Flow):
    '''
    The standard actor class.
    '''
    pass


class Specialist(BPI13Flow):
    '''
    Special actor with extra actions only specialists can execute.
    TODO: should CustomerServiceActors have these too, so that some of the variance in our model can be unauthorised
    people performing these actions?
    '''

    def W_valideren_aanvraag_start(self):
        pass

    def W_valideren_aanvraag_complete(self):
        pass

    def A_approved(self):
        pass

    def A_activated(self):
        pass

    def A_registered(self):
        pass

    def O_declined(self):
        pass

    def O_accepted(self):
        pass

