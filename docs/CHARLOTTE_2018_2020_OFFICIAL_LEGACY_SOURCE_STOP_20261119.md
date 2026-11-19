# SWFWMD 2018/2020 official map source — historical verification STOP (2026-11-19)

The officially advertised SWFWMD Environmental_Seagrass2018_sql MapServer lists 2018 layer 0, 2020 layer 1, 2022 layer 2 and 2024 layer 3:
https://www45.swfwmd.state.fl.us/arcgis12/rest/services/OpenData/Environmental_Seagrass2018_sql/MapServer

To test whether 2022–2024 Charlotte mapped algae/seagrass changes recur in a prior interval, the source-only code analysis/110_charlotte_2018_2020_legacy_map_preflight.py froze these two older years, class codes 9113/9116/9121, and the earlier verified Charlotte 2016/2022/2024 envelope before opening category values. It verifies the source date, official polygon schema and declared CRS and attempts only metadata and category counts, not raw polygon geometry.

## Observed failure, not biological evidence

First official FeatureServer /0 returned a JSON object with status and messages keys rather than a valid 2018 Feature Layer response: SOURCE_YEAR_OR_POLYGON_IDENTITY_DRIFT:2018. A separately documented access-path correction tried the *same official service data family* via MapServer /0; it likewise returned only status/messages instead of layer metadata.

Documented stopped Actions runs:
- Original FeatureServer source check: https://github.com/zuizui0223/Tampa/actions/runs/44463783529
- Diagnostic of actual returned keys: https://github.com/zuizui0223/Tampa/actions/runs/44463927903
- Same official MapServer source gate: https://github.com/zuizui0223/Tampa/actions/runs/44464190289

**Status:** 2018 layer identity and geometry remain unverified and the first source-date gate failed. 2020 has not been empirically evaluated because 2018 stopped first. This is a source accessibility failure, *not* evidence of zero mapped algae in either year, no historical class change, failed biological hypothesis, or permanent loss of public official records. Do not interpolate unknown dates or switch to a favorable bay.

The already source-audited official 2016 positive seagrass and 2022/2024 polygons remain inspectable in their frozen successful GitHub Actions archives. Those older source digests were obtained before the legacy live API began returning changed/unusable responses.

Future authorized 2018/2020 original file or service exports require independent spatial footprint, map classification dictionary, source acreage and exact OID checks before inferential comparison. No true field-algal abundance or sea-shoot turnover has been observed through these failed older-year requests.
