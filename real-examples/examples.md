# example1.json

Archetype: Clusters. Many different services, perhaps even environments, mapped in one. For Terraform export, I think the user would select a subset of the diagram in Cloudcraft.

# example2.json

Archetype: Spider web. Every single resource from a current environment with minimal regard for layout. Useful for re-creating or snapshotting an environment if it could be re-exported to Terraform or CF.

# example3.json

Archetype: Structured single service. Well designed, single-service diagram. This is probably close to the ideal user. Typically segments components by subnet or security groups (which Cloudcraft currently lacks components for, that I’m however working on).