import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Header,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  Content,
  Theme,
} from '@carbon/react'

interface LayoutProps {
  children: ReactNode
}

const navItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Accounts', path: '/accounts' },
  { label: 'Transcripts', path: '/transcripts' },
  { label: 'Opportunities', path: '/opportunities' },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <Theme theme="g100">
      <Header aria-label="CommAi">
        <HeaderName href="/dashboard" prefix="IBM">
          CommAi
        </HeaderName>
        <HeaderNavigation aria-label="Main navigation">
          {navItems.map(item => (
            <HeaderMenuItem
              key={item.path}
              as={Link}
              to={item.path}
              isCurrentPage={location.pathname.startsWith(item.path)}
            >
              {item.label}
            </HeaderMenuItem>
          ))}
        </HeaderNavigation>
      </Header>
      <Theme theme="white">
        <Content style={{ paddingTop: '3rem' }}>
          {children}
        </Content>
      </Theme>
    </Theme>
  )
}
