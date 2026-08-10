import { notFound, redirect } from "next/navigation";

type Props = { params: Promise<{ state: string }> };

export default async function StateAliasPage({ params }: Props) {
  const { state } = await params;
  if (state === "california") redirect("/california");
  notFound();
}
