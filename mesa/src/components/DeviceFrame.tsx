import type { ReactNode } from "react";

// The physical unit: a dark metal panel with a bezel and four corner screws.
export default function DeviceFrame({ children }: { children: ReactNode }) {
  return (
    <div className="device-outer">
      <div className="device">
        <span className="screw tl" /><span className="screw tr" />
        <span className="screw bl" /><span className="screw br" />
        <div className="device-inner">{children}</div>
      </div>
    </div>
  );
}
