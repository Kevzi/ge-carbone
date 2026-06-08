from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.carbon_engine.models import CarbonFeedback
from apps.carbon_engine.services.anonymiser import FECAnonymiser

class FeedbackCreateView(APIView):
    """
    POST: Submit feedback to improve NLP mapping.
    Anonymizes the data (RGPD) before storing it.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        original_compte_num = request.data.get('compte_num', '')
        original_ecriture_lib = request.data.get('ecriture_lib', '')
        corrected_category = request.data.get('corrected_category', '')
        corrected_ademe_id = request.data.get('corrected_ademe_id', '')
        try:
            corrected_dqr = int(request.data.get('corrected_dqr', 3))
            if corrected_dqr not in [1, 2, 3]:
                corrected_dqr = 3
        except (TypeError, ValueError):
            corrected_dqr = 3
        if not corrected_category:
            return Response({'error': 'La catégorie corrigée est requise.'}, status=status.HTTP_400_BAD_REQUEST)

        # Anonymiser les données via FEC_Anonymiser
        anon_compte, anon_libelle = FECAnonymiser.prepare_feedback_data(original_compte_num, original_ecriture_lib)

        # Création du feedback
        feedback = CarbonFeedback.objects.create(
            original_compte_num=anon_compte,
            original_ecriture_lib=anon_libelle,
            corrected_category=corrected_category,
            corrected_ademe_id=corrected_ademe_id,
            corrected_dqr=corrected_dqr
        )

        return Response({
            'message': 'Feedback enregistré avec succès (données anonymisées).',
            'feedback_id': feedback.id
        }, status=status.HTTP_201_CREATED)
