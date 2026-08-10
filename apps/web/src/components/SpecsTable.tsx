import type { DisposalPage } from "@/lib/types";

export function SpecsTable({ page }: { page: DisposalPage }) {
  const rows = [
    {
      label: "Curbside pickup",
      value: page.is_curbside_allowed ? "Yes / organics stream" : "No / special call or drop-off required",
    },
    { label: "Average tipping fee", value: page.common_disposal_fee },
    { label: "Hazardous rating", value: page.hazard_rating },
    { label: "Nearest facility type", value: page.nearest_facility_type },
    { label: "Rule source level", value: page.rule_source_level },
    {
      label: "Last verified",
      value: page.last_verified_at ?? "Not yet locally verified",
    },
  ];
  return (
    <table className="specs-table">
      <tbody>
        {rows.map((r) => (
          <tr key={r.label}>
            <th scope="row">{r.label}</th>
            <td>{r.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
