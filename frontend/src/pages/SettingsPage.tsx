import React, { useState } from 'react';
import { Button } from '../components/common/Button';
import { ShieldCheck, HardDrive, Cpu, Terminal } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [cacheRetention, setCacheRetention] = useState('30');
  const [coordinateSystem, setCoordinateSystem] = useState('WGS84');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  const handleClearCache = () => {
    if (confirm('Clear local raster cache and temporary satellite tiles?')) {
      alert('Local cache pruned. Zero persistent investigation records affected.');
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1 style={{ fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          System & Analytical Configuration
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          Geodetic datums, raster pipeline cache, and reproducibility settings.
        </p>
      </div>

      {savedSuccess && (
        <div
          style={{
            padding: '10px 14px',
            backgroundColor: 'var(--color-success-subtle)',
            border: '1px solid var(--color-success-border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--color-success)',
            fontSize: '13px',
            marginBottom: 'var(--space-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <ShieldCheck size={16} /> Configuration updated successfully.
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
        {/* Geodetic Reference */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-md)' }}>
            <Cpu size={16} style={{ color: 'var(--color-primary)' }} />
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Coordinate Reference System (CRS)</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            <label style={{ fontSize: '12px', fontWeight: 500 }}>Default Geospatial Projection</label>
            <select
              value={coordinateSystem}
              onChange={(e) => setCoordinateSystem(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                maxWidth: '300px',
              }}
            >
              <option value="WGS84">EPSG:4326 - WGS 84 (Default World Geodetic)</option>
              <option value="WEB_MERCATOR">EPSG:3857 - WGS 84 / Pseudo-Mercator</option>
              <option value="UTM_AUTO">Universal Transverse Mercator (Auto UTM Zone)</option>
            </select>
            <p style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              All internal vector bounds are standardized to EPSG:4326 before pipeline submission.
            </p>
          </div>
        </section>

        {/* Caching and Local Storage */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-md)' }}>
            <HardDrive size={16} style={{ color: 'var(--color-primary)' }} />
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Tile Cache & Memory Retention</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ fontSize: '12px', fontWeight: 500, display: 'block', marginBottom: '4px' }}>
                Copernicus / Landsat Tile Cache Retention (Days)
              </label>
              <input
                type="number"
                min="1"
                max="180"
                value={cacheRetention}
                onChange={(e) => setCacheRetention(e.target.value)}
                style={{
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  maxWidth: '120px',
                }}
              />
            </div>

            <div style={{ paddingTop: 'var(--space-sm)', borderTop: '1px solid var(--color-border-subtle)' }}>
              <Button type="button" variant="outline" size="sm" onClick={handleClearCache}>
                Prune Offline Raster Tiles
              </Button>
            </div>
          </div>
        </section>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button type="submit" variant="primary">
            Save Preferences
          </Button>
        </div>
      </form>
    </div>
  );
};

