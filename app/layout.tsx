import type { ReactNode } from 'react';
export default function RootLayout({children}: {children: ReactNode}) {
 return <html lang="hi"><head><meta name="viewport" content="width=device-width,initial-scale=1"/><link rel="stylesheet" href="/styles.css"/><link rel="stylesheet" href="/layout.css"/><link rel="stylesheet" href="/account.css"/></head><body>{children}</body></html>;
}
