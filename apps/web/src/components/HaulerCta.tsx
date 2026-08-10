import Link from "next/link";

export function HaulerCta({ city, stateSlug }: { city: string; stateSlug: string }) {
  const href = `/partners?city=${encodeURIComponent(city)}&state=${encodeURIComponent(stateSlug)}`;
  return (
    <section className="hauler-cta" aria-labelledby="hauler-cta-heading">
      <h2 id="hauler-cta-heading">Haulers serving {city}</h2>
      <p>
        Get pickup requests from residents who already looked up disposal rules here. Apply once — onboard by
        email.
      </p>
      <Link className="btn-secondary" href={href}>
        Partner in {city}
      </Link>
    </section>
  );
}
