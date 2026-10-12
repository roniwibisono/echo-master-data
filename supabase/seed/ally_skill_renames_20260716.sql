begin;

update public.skills
set name = v.name
from (
  values
    ('al5_67_act', 'Dockside Absolution'),
    ('al5_68_pas', 'Jury-Rigged Surge'),
    ('al5_73_pas', 'Unfinished Charge'),
    ('al5_80_pas', 'Corporate Bulwark'),
    ('al5_88_pas', 'Seventh Protocol'),
    ('al5_90_pas', 'Centuries of Aegis'),
    ('al5_91_pas', 'Prewar Benediction')
) as v(id, name)
where public.skills.id = v.id;

commit;
