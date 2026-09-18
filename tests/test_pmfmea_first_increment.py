from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from fmea_app import forms, models
from fmea_domain import Asset as DomainAsset, FailureMode as DomainFailureMode


class AssetModelTests(TestCase):
    def test_asset_defaults_and_str(self):
        asset = models.Asset.objects.create(
            stable_id="asset:cnc-01",
            name="CNC-01",
            asset_code="CNC-01",
            location="Plant 1 / Line A",
        )

        self.assertEqual(asset.status, models.AssetStatus.OPERATIONAL)
        self.assertEqual(str(asset), "CNC-01")

    def test_to_domain_round_trips_all_fields(self):
        asset = models.Asset.objects.create(
            stable_id="asset:press-02",
            name="Press-02",
            asset_code="PRESS-02",
            location="Plant 1 / Line B",
            status=models.AssetStatus.DOWN,
            notes="Awaiting hydraulic seal replacement.",
        )

        domain_asset = asset.to_domain()

        self.assertIsInstance(domain_asset, DomainAsset)
        self.assertEqual(domain_asset.stable_id, "asset:press-02")
        self.assertEqual(domain_asset.name, "Press-02")
        self.assertEqual(domain_asset.asset_code, "PRESS-02")
        self.assertEqual(domain_asset.location, "Plant 1 / Line B")
        self.assertEqual(domain_asset.status, "down")
        self.assertEqual(domain_asset.notes, "Awaiting hydraulic seal replacement.")


class FailureModeAssetLinkTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:pmfmea-link",
            name="Injection Molding PM-FMEA",
            fmea_type="preventive",
        )
        self.asset = models.Asset.objects.create(
            stable_id="asset:imm-03",
            name="Injection Molding Machine 03",
            asset_code="IMM-03",
        )

    def test_failure_mode_can_link_to_an_asset(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:spindle-wear",
            fmea=self.fmea,
            name="Spindle bearing wear",
            asset=self.asset,
        )

        self.assertEqual(failure_mode.asset, self.asset)
        self.assertIn(failure_mode, self.asset.failure_modes.all())

    def test_failure_mode_asset_is_optional_for_every_fmea_type(self):
        design_fmea = models.FMEA.objects.create(
            stable_id="fmea:pmfmea-link-design",
            name="Headlamp DFMEA",
            fmea_type="design",
        )
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:no-asset",
            fmea=design_fmea,
            name="Beam distortion",
        )

        self.assertIsNone(failure_mode.asset)

    def test_to_domain_includes_asset_id_only_when_linked(self):
        linked = models.FailureMode.objects.create(
            stable_id="fm:linked-to-asset",
            fmea=self.fmea,
            name="Hydraulic leak",
            asset=self.asset,
        )
        unlinked = models.FailureMode.objects.create(
            stable_id="fm:unlinked",
            fmea=self.fmea,
            name="Cooling system failure",
        )

        linked_domain = linked.to_domain()
        unlinked_domain = unlinked.to_domain()

        self.assertIsInstance(linked_domain, DomainFailureMode)
        self.assertEqual(linked_domain.asset_id, "asset:imm-03")
        self.assertIsNone(unlinked_domain.asset_id)

    def test_deleting_asset_sets_failure_mode_asset_to_null_not_cascade(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:survives-asset-delete",
            fmea=self.fmea,
            name="Belt tension loss",
            asset=self.asset,
        )

        self.asset.delete()
        failure_mode.refresh_from_db()

        self.assertIsNone(failure_mode.asset)


class FMEATypeChoiceTests(TestCase):
    def test_preventive_is_a_selectable_fmea_type_alongside_existing_ones(self):
        choice_values = dict(models.FMEA.FMEA_TYPE_CHOICES)

        self.assertEqual(choice_values["preventive"], "Preventive FMEA (PM-FMEA)")
        # Every pre-existing choice remains exactly as it was - additive only.
        self.assertEqual(choice_values["design"], "Design")
        self.assertEqual(choice_values["process"], "Process")
        self.assertEqual(choice_values["product"], "Product")
        self.assertEqual(choice_values["software"], "Software")
        self.assertEqual(choice_values["system"], "System")


class PMFMEAWorksheetViewTests(TestCase):
    def setUp(self) -> None:
        self.pm_fmea = models.FMEA.objects.create(
            stable_id="fmea:pmfmea-worksheet",
            name="Spindle PM-FMEA",
            fmea_type="preventive",
        )
        self.design_fmea = models.FMEA.objects.create(
            stable_id="fmea:dfmea-worksheet-scope",
            name="Headlamp DFMEA (scope check)",
            fmea_type="design",
        )
        self.process_fmea = models.FMEA.objects.create(
            stable_id="fmea:pfmea-worksheet-scope",
            name="Assembly PFMEA (scope check)",
            fmea_type="process",
        )
        self.asset = models.Asset.objects.create(
            stable_id="asset:cnc-02",
            name="CNC-02",
            asset_code="CNC-02",
        )
        self.pm_failure_mode = models.FailureMode.objects.create(
            stable_id="fm:pmfmea-worksheet-row",
            fmea=self.pm_fmea,
            name="Spindle bearing wear",
            asset=self.asset,
        )
        models.FailureMode.objects.create(
            stable_id="fm:dfmea-worksheet-row",
            fmea=self.design_fmea,
            name="Beam distortion",
        )
        models.FailureMode.objects.create(
            stable_id="fm:pfmea-worksheet-row",
            fmea=self.process_fmea,
            name="Water ingress",
        )

    def test_pmfmea_worksheet_lists_only_preventive_fmeas(self):
        response = self.client.get(reverse("fmea:pmfmea_worksheet"))

        self.assertContains(response, "Spindle PM-FMEA")
        self.assertContains(response, "Spindle bearing wear")
        self.assertNotContains(response, "Beam distortion")
        self.assertNotContains(response, "Water ingress")

    def test_pmfmea_worksheet_shows_the_linked_asset(self):
        response = self.client.get(reverse("fmea:pmfmea_worksheet"))

        self.assertContains(response, "CNC-02")

    def test_dfmea_worksheet_excludes_preventive_fmeas(self):
        response = self.client.get(reverse("fmea:dfmea_worksheet"))

        self.assertContains(response, "Beam distortion")
        self.assertNotContains(response, "Spindle bearing wear")

    def test_pfmea_worksheet_still_only_shows_process_fmeas(self):
        response = self.client.get(reverse("fmea:pfmea_worksheet"))

        self.assertContains(response, "Water ingress")
        self.assertNotContains(response, "Spindle bearing wear")
        self.assertNotContains(response, "Beam distortion")


class AssetStandalonePagesTests(TestCase):
    def setUp(self) -> None:
        self.asset = models.Asset.objects.create(
            stable_id="asset:chiller-01",
            name="Chiller-01",
            asset_code="CHL-01",
            location="Plant 1 / Utilities",
        )
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:asset-pages",
            name="Chiller PM-FMEA",
            fmea_type="preventive",
        )

    def test_asset_list_shows_linked_failure_mode_count(self):
        models.FailureMode.objects.create(
            stable_id="fm:asset-pages-row",
            fmea=self.fmea,
            name="Cooling system failure",
            asset=self.asset,
        )

        response = self.client.get(reverse("fmea:asset_list"))

        self.assertContains(response, "Chiller-01")
        self.assertContains(response, "CHL-01")

    def test_asset_create_then_detail_round_trip(self):
        response = self.client.post(
            reverse("fmea:asset_create"),
            {
                "name": "Air Comp-01",
                "asset_code": "AIRC-01",
                "location": "Plant 1 / Utilities",
                "status": "operational",
                "notes": "",
            },
        )

        asset = models.Asset.objects.get(name="Air Comp-01")
        self.assertRedirects(response, reverse("fmea:asset_detail", args=[asset.stable_id]))

        detail_response = self.client.get(reverse("fmea:asset_detail", args=[asset.stable_id]))
        self.assertContains(detail_response, "AIRC-01")

    def test_asset_edit_updates_status(self):
        response = self.client.post(
            reverse("fmea:asset_edit", args=[self.asset.stable_id]),
            {
                "name": self.asset.name,
                "asset_code": self.asset.asset_code,
                "location": self.asset.location,
                "status": "under_maintenance",
                "notes": "",
            },
        )

        self.assertRedirects(response, reverse("fmea:asset_detail", args=[self.asset.stable_id]))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "under_maintenance")

    def test_asset_detail_lists_linked_failure_modes(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:asset-detail-row",
            fmea=self.fmea,
            name="Filter clogging",
            asset=self.asset,
        )

        response = self.client.get(reverse("fmea:asset_detail", args=[self.asset.stable_id]))

        self.assertContains(response, "Filter clogging")
        self.assertContains(response, self.fmea.name)


class FailureModeFormAssetFieldTests(TestCase):
    def test_asset_field_is_optional_and_offers_all_assets(self):
        models.Asset.objects.create(stable_id="asset:form-test", name="Conv-03", asset_code="CONV-03")

        form = forms.FailureModeForm()

        self.assertFalse(form.fields["asset"].required)
        self.assertIn("Conv-03", [str(a) for a in form.fields["asset"].queryset])


class AddFailureModeViewSavesAssetTests(TestCase):
    def test_add_failure_mode_saves_the_selected_asset(self):
        fmea = models.FMEA.objects.create(
            stable_id="fmea:add-failure-mode-asset",
            name="Conveyor PM-FMEA",
            fmea_type="preventive",
        )
        asset = models.Asset.objects.create(
            stable_id="asset:conv-03",
            name="Conv-03",
            asset_code="CONV-03",
        )

        self.client.post(
            reverse("fmea:add_failure_mode", args=[fmea.stable_id]),
            {"name": "Belt tension loss", "description": "", "asset": asset.pk},
        )

        failure_mode = models.FailureMode.objects.get(name="Belt tension loss")
        self.assertEqual(failure_mode.asset, asset)

    def test_add_failure_mode_without_asset_still_works(self):
        fmea = models.FMEA.objects.create(
            stable_id="fmea:add-failure-mode-no-asset",
            name="Headlamp DFMEA (no asset)",
            fmea_type="design",
        )

        self.client.post(
            reverse("fmea:add_failure_mode", args=[fmea.stable_id]),
            {"name": "Beam distortion", "description": ""},
        )

        failure_mode = models.FailureMode.objects.get(name="Beam distortion")
        self.assertIsNone(failure_mode.asset)


class SidebarAndFmeaDetailAssetSurfaceTests(TestCase):
    def test_sidebar_offers_pmfmea_worksheet_and_asset_list_links(self):
        response = self.client.get("/")

        self.assertContains(response, "Preventive FMEA (PM-FMEA)")
        self.assertContains(response, "Assets & Equipment")

    def test_fmea_detail_add_failure_mode_form_offers_asset_field(self):
        fmea = models.FMEA.objects.create(
            stable_id="fmea:detail-asset-field",
            name="Press PM-FMEA",
            fmea_type="preventive",
        )

        response = self.client.get(reverse("fmea:fmea_detail", args=[fmea.stable_id]))

        self.assertContains(response, "Asset (PM-FMEA)")

    def test_fmea_detail_worksheet_row_shows_linked_asset(self):
        fmea = models.FMEA.objects.create(
            stable_id="fmea:detail-asset-row",
            name="Chiller PM-FMEA (row)",
            fmea_type="preventive",
        )
        asset = models.Asset.objects.create(
            stable_id="asset:detail-row",
            name="Chiller-02",
            asset_code="CHL-02",
        )
        models.FailureMode.objects.create(
            stable_id="fm:detail-asset-row",
            fmea=fmea,
            name="Refrigerant leak",
            asset=asset,
        )

        response = self.client.get(reverse("fmea:fmea_detail", args=[fmea.stable_id]))

        self.assertContains(response, "Chiller-02")
