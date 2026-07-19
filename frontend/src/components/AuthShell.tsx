import type { ReactNode } from "react";
import banner from "../assets/brand/bbb-consig-banner.png";
import bannerDesktop from "../assets/brand/bbb-consig-banner-1200.webp";
import bannerMobile from "../assets/brand/bbb-consig-banner-768.webp";
import { BrandLogo } from "./ui/BrandLogo";

type AuthShellProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
};

export function AuthShell({ title, subtitle, children }: AuthShellProps) {
  return (
    <main className="auth-page min-h-screen px-4 py-6 sm:px-6">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-6xl items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="order-2 hidden min-h-[560px] overflow-hidden rounded-[28px] border border-white/70 bg-white shadow-[var(--bbb-shadow-raised)] lg:block">
          <picture>
            <source srcSet={`${bannerMobile} 768w, ${bannerDesktop} 1200w`} type="image/webp" sizes="(min-width: 1024px) 50vw, 100vw" />
            <img
              className="h-full w-full object-cover"
              src={banner}
              alt="Identidade visual BBB Consig"
              width="1600"
              height="667"
            />
          </picture>
        </section>
        <section className="order-1 mx-auto w-full max-w-xl rounded-[24px] border border-[var(--bbb-line)] bg-white p-5 shadow-[var(--bbb-shadow-panel)] sm:p-7">
          <BrandLogo />
          <div className="mt-8">
            <p className="text-xs font-bold uppercase text-[var(--bbb-orange)]">Acesso seguro</p>
            <h1 className="mt-2 text-3xl font-extrabold text-slate-950 sm:text-4xl">{title}</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">{subtitle}</p>
          </div>
          <div className="mt-7">{children}</div>
        </section>
      </div>
    </main>
  );
}
